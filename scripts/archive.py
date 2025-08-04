# Contains shared utility functions for the WCP toolkit.

import os
import tarfile
import zstandard as zstd

def create_wcp_archive(source_dir, output_path):
    """
    Creates a .tar.zst archive (the .wcp format) from a source directory.
    This function is shared by all converter scripts.
    """
    print(f"Creating archive at: {output_path}")
    
    # Initialize the Zstandard compressor with a good compression level and multi-threading.
    cctx = zstd.ZstdCompressor(level=3, threads=-1)

    # Open the target file in binary write mode to write the compressed data.
    with open(output_path, 'wb') as f_out:
        # Use the Zstandard stream writer to compress data on the fly.
        with cctx.stream_writer(f_out) as compressor:
            # Create a streaming tarball writer that sends its output to the compressor.
            with tarfile.open(mode='w|', fileobj=compressor) as tar:
                # Iterate over all items in the source directory to be packaged.
                for item in os.listdir(source_dir):
                    # Add the item to the tar archive, using its own name as the name inside the archive.
                    tar.add(os.path.join(source_dir, item), arcname=item)
                    
    print("Archive created successfully.")