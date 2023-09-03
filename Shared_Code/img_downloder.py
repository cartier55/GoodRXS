from urllib.parse import urlparse
import httpx
import asyncio
import pandas as pd
from tqdm import tqdm
import os
from img_logger import ImgDLoaderLogger


async def download_image(session, url, file_path, semaphore, logger, pbar):
    async with semaphore:
        try:
            response = await session.get(url)
            data = response.content
            with open(file_path, 'wb') as f:
                f.write(data)
            logger.log_info(f"Downloaded image from {url}")
            pbar.update()  # This will update the progress bar each time an image is successfully downloaded
            return None  # return None on success
        except httpx.RequestError as exc:
            print(f"An error occurred while downloading {url}: {exc}")
            logger.log_error(f"An error occurred while downloading {url}: {exc}")
            return url  # return the failed url

async def main(file_path, max_concurrent_downloads):
    logger = ImgDLoaderLogger()
    df = pd.read_csv(file_path)

    # Convert image_url column to a set to get unique URLs
    unique_urls = set(df['image_url'].dropna())

    logger.log_info(f"Starting image download with {file_path}")
    logger.log_info(f"Starting image download for {len(unique_urls)} drugs")
    logger.log_info(f"Max concurrent downloads: {max_concurrent_downloads}")

    semaphore = asyncio.Semaphore(max_concurrent_downloads)
    async with httpx.AsyncClient() as session:
        tasks = []
        pbar = tqdm(total=len(unique_urls), desc="Downloading images")
        for i, url in enumerate(unique_urls):
            if pd.isna(url):
                logger.log_info(f"Skipping row {i} because image_url is NaN")
                continue
            filename = os.path.basename(url)
            image_file_path = os.path.join('results/images', filename)
            tasks.append(download_image(session, url, image_file_path, semaphore, logger, pbar))
        results = await asyncio.gather(*tasks)
        pbar.close()
        # retry failed urls
        failed_urls = [url for url in results if url is not None]
        if failed_urls:
            print(f"Retrying {len(failed_urls)} failed URLs...")
            logger.log_info(f"Retrying {len(failed_urls)} failed URLs...")
            retry_tasks = []
            for url in tqdm(failed_urls, desc="Retrying failed URLs"):
                filename = os.path.basename(url)
                image_file_path = os.path.join('results/images', filename)
                retry_tasks.append(download_image(
                    session, url, image_file_path, semaphore, logger, pbar))
            retry_results = await asyncio.gather(*retry_tasks)

            # log the failed retry attempts
            failed_retries = [url for url in retry_results if url is not None]
            if failed_retries:
                logger.log_error(
                    f"Retry failed : {failed_retries}")
# asyncio.run(main('your_file.csv', 10))


asyncio.run(main('./results/drug_info/all_drug_infos_complete_copy.csv', 50))


# i - Formats info csv image_url column


def modify_image_urls(df):
    # Extract the last part of the URL path and add '/images/' before it
    df['image_url'] = df['image_url'].apply(
        lambda url: '/images/' + os.path.basename(urlparse(url).path) if pd.notnull(url) else url)

    return df

# df = pd.read_csv('./results/drug_info/all_drug_infos_complete.csv')

# print(df.head())

# Apply the function to the DataFrame
# df_modified = modify_image_urls(df)

# Display the first few rows of the modified DataFrame
# print(df_modified['image_url'].head())
# df_modified.to_csv('./results/drug_info/all_drug_infos_complete.csv', index=False)
