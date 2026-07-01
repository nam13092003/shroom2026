import os
import hydra
from omegaconf import DictConfig, OmegaConf
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

try:
    import pytorch_lightning as pl
    from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor
    from pytorch_lightning.loggers import TensorBoardLogger
except ImportError:
    # Lightning not installed in current environment, define dummies
    pl = None

from datasets.shroom_dataset import ShroomVisionsDataset, ShroomVisionsCollator
from trainer.lightning_module import ShroomVisionsModule

@hydra.main(config_path="../configs", config_name="config", version_base="1.1")
def main(cfg: DictConfig):
    # Print configuration
    print("=" * 60)
    print("SHROOM-Vision 2026 Multitask Training Initialization")
    print("=" * 60)
    print(OmegaConf.to_yaml(cfg))
    print("=" * 60)

    # Set random seed
    pl.seed_everything(cfg.get('seed', 42))

    # Initialize tokenizer
    print("Loading tokenizer...")
    # Using Qwen2.5-VL tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        "Qwen/Qwen2.5-VL-7B-Instruct",
        trust_remote_code=True
    )
    # Ensure pad token is set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 1. Create datasets
    print("Creating datasets...")
    train_dataset = ShroomVisionsDataset(
        jsonl_path=cfg.train_jsonl_path,
        images_dir=cfg.images_dir,
        tokenizer=tokenizer,
        cache_dir=cfg.get('cache_dir', None),
        max_length=cfg.get('max_length', 1024),
        is_training=True
    )

    val_dataset = ShroomVisionsDataset(
        jsonl_path=cfg.val_jsonl_path,
        images_dir=cfg.images_dir,
        tokenizer=tokenizer,
        cache_dir=cfg.get('cache_dir', None),
        max_length=cfg.get('max_length', 1024),
        is_training=False
    )

    # 2. Create dataloaders
    collator = ShroomVisionsCollator(pad_token_id=tokenizer.pad_token_id)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.get('num_workers', 4),
        collate_fn=collator,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=cfg.batch_size,
        shuffle=False,
        num_workers=cfg.get('num_workers', 4),
        collate_fn=collator,
        pin_memory=True
    )

    # 3. Create Lightning Module
    print("Building Lightning Module...")
    # Convert DictConfig to raw dict
    config_dict = OmegaConf.to_container(cfg, resolve=True)
    model_module = ShroomVisionsModule(config_dict)

    # 4. Set up callbacks and loggers
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)
    os.makedirs(cfg.log_dir, exist_ok=True)

    checkpoint_callback = ModelCheckpoint(
        dirpath=cfg.checkpoint_dir,
        filename="best-shroom-visions-{epoch:02d}-{val_char_iou:.4f}",
        monitor="val_char_iou",
        mode="max",
        save_top_k=1,
        verbose=True
    )

    early_stopping = EarlyStopping(
        monitor="val_char_iou",
        patience=cfg.early_stopping_patience,
        mode="max",
        verbose=True
    )

    lr_monitor = LearningRateMonitor(logging_interval='epoch')
    
    logger = TensorBoardLogger(
        save_dir=cfg.log_dir,
        name="shroom_multitask_probing"
    )

    # 5. Initialize Lightning Trainer
    # Plugs in mixed precision (bf16/fp16), DDP/DeepSpeed or standard single-gpu from config
    print("Initializing trainer...")
    trainer = pl.Trainer(
        max_epochs=cfg.max_epochs,
        devices=cfg.devices,
        accelerator=cfg.accelerator,
        precision=cfg.precision,
        accumulate_grad_batches=cfg.accumulate_grad_batches,
        gradient_clip_val=cfg.gradient_clip_val,
        callbacks=[checkpoint_callback, early_stopping, lr_monitor],
        logger=logger,
        log_every_n_steps=10
    )

    # 6. Start training
    print("🚀 Starting training...")
    trainer.fit(model_module, train_loader, val_loader)
    print("Training completed successfully!")

if __name__ == "__main__":
    if pl is None:
        raise ImportError("pytorch-lightning is required to run the train entrypoint script.")
    main()
