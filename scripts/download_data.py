import os
import ssl
import zipfile
import tarfile
import urllib.request
from tqdm import tqdm

def download_file(url, output_path):
    print(f"Downloading {url} to {output_path}...")
    ctx = ssl._create_unverified_context()
    
    # Custom opener to handle progress tracking
    class ProgressTracker:
        def __init__(self):
            self.pbar = None
            
        def __call__(self, block_num, block_size, total_size):
            if self.pbar is None:
                self.pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(output_path))
            downloaded = block_num * block_size
            if downloaded < total_size:
                self.pbar.n = downloaded
                self.pbar.refresh()
            else:
                self.pbar.n = total_size
                self.pbar.close()

    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    urllib.request.install_opener(opener)
    
    tracker = ProgressTracker()
    urllib.request.urlretrieve(url, output_path, reporthook=tracker)
    print(f"Finished downloading {output_path}")

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path} to {extract_to}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")

def extract_tar(tar_path, extract_to):
    print(f"Extracting {tar_path} to {extract_to}...")
    with tarfile.open(tar_path, "r:gz") as tar_ref:
        tar_ref.extractall(extract_to)
    print("Extraction complete.")

def main():
    # Dynamically locate the data directory relative to repository root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Download and extract annotations
    data_zip = os.path.join(data_dir, "shroom-visions-data.zip")
    data_url = "https://a3s.fi/mickusti-2007780-pub/shroom-visions-data.zip"
    if not os.path.exists(data_zip):
        download_file(data_url, data_zip)
    extract_zip(data_zip, data_dir)
    
    # Download and extract images
    images_tar = os.path.join(data_dir, "shroom-visions-images.tar.gz")
    images_url = "https://a3s.fi/mickusti-2007780-pub/shroom-visions-images.tar.gz"
    if not os.path.exists(images_tar):
        download_file(images_url, images_tar)
    extract_tar(images_tar, data_dir)

if __name__ == "__main__":
    main()
