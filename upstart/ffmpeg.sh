sudo apt-get update
sudo apt-get -y install autoconf automake build-essential libass-dev libfreetype6-dev libsdl1.2-dev libtheora-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev libxcb-xfixes0-dev pkg-config texinfo zlib1g-dev
sudo apt-get install yasm
sudo apt-get install libx264-dev
sudo apt-get install cmake mercurial
#mkdir ~/ffmpeg-sources
cd ~/ffmpeg-sources
hg clone https://bitbucket.org/multicoreware/x265
cd ~/ffmpeg-sources/x265/build/linux
#PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_SHARED:bool=off ../../source
PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DENABLE_SHARED:bool=off ../../source
make 
sudo make install
make distclean
sudo apt-get install libfdk-aac-dev
sudo apt-get install libmp3lame-dev
sudo apt-get install libopus-dev
cd ~/ffmpeg_sources
wget http://storage.googleapis.com/downloads.webmproject.org/releases/webm/libvpx-1.6.0.tar.bz2
tar xjvf libvpx-1.6.0.tar.bz2
cd libvpx-1.6.0
PATH="$HOME/bin:$PATH" ./configure  --disable-examples --disable-unit-tests
PATH="$HOME/bin:$PATH" make
sudo make install
make clean
cd ~/ffmpeg_sources
wget http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg
PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
  --pkg-config-flags="--static" \
  --extra-cflags="-I$HOME/ffmpeg_build/include" \
  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
  --bindir="$HOME/bin" \
  --enable-gpl \
  --enable-libass \
  --enable-libfdk-aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libtheora \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-nonfree
PATH="$HOME/bin:$PATH" make
sudo make install
make distclean
hash -r
