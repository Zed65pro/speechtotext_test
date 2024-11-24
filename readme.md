For testing whisper have to setup ffmpeg


# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg


For nlpcloud please replace the token in .env with token from https://nlpcloud.com/home/token


to use sina tools use commands:
download_files -f morph ner wsd synonyms

after download SinaTools package, or you can download only the files that you require, this is needed to run sonatools

and sinatools depends on torch=1.13.0

to use sinatools disambiguate have to install PyArabic and Pandas and downgrade numpy to 1.*

Include google credentials json inside root directory