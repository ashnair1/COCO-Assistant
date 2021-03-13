import requests
import tarfile


def download_file_from_google_drive(fid, destination):
    url = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(url, params={"id": fid}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": fid, "confirm": token}
        response = session.get(url, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None


def save_response_content(response, destination):
    chunk_size = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


if __name__ == "__main__":
    file_id = "1JJoeO9FQ9vAdmhALma7wpgqs3OTTPPwF"
    destination = "test.tar.gz"
    download_file_from_google_drive(file_id, destination)
    # Unzip data
    tar = tarfile.open(destination, "r:gz")
    tar.extractall()
    tar.close()
