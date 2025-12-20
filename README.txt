====== SequenceTree4 Installation ======

==== Linux (tested with Pop! OS 22.04 LTS) ====

Install FFTW (tested with 3.3.10)
  0. Download fftw at http://www.fftw.org/
  1. Extract contents to folder
  2. cd to FFTW folder
  3. $./configure
  4. $make
  5. $sudo make install


Install GNU Scientific Library (tested with 2.8)
  0. Download GNU Scientific Library at https://ftp.gnu.org/gnu/gsl/
  1. Extract contents to folder
  2. cd to GSL folder
  3. $./configure
  4. $make
  5. $sudo make install


Install Git
  0. $sudo apt-get install git


Install Qt5
  0. $sudo apt-get install qtcreator qtbase5-dev qt5-qmake cmake


Download and install SequenceTree 4
  0. $git clone https://github.com/btdvu/sequencetree4.git
  1. $cd sequencetree4/src
  2. $qmake
  3. $make
  4. $cd ..
  5. $mkdir tmp

Run SequenceTree 4
  0. $cd sequencetree4/bin
  1. $./st4


==== macOS (tested with Sequoia 15.7.3 on Apple M4 Max) ====

Install Xcode Command Line Tools
  0. Open Terminal
  1. $xcode-select --install
  2. Follow the on‑screen prompts to finish installation

Install Homebrew
  0. Open Terminal
  1. $/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  2. When installation finishes, follow any instructions printed to add Homebrew to your shell, then open a new Terminal window

Install FFTW (via Homebrew)
  0. $brew install fftw
​
Install GNU Scientific Library (via Homebrew)
  0. $brew install gsl
​
Install Git (via Homebrew)
  0. $brew install git

Install Qt5 (qt@5)
  0. $brew install qt@5
  1. For Apple Silicon (M‑series), add Qt5 to PATH:
  $echo 'export PATH="/opt/homebrew/opt/qt@5/bin:$PATH"' >> ~/.zshrc
  OR
  For Intel Macs, add Qt5 to PATH instead:
  $echo 'export PATH="/usr/local/opt/qt@5/bin:$PATH"' >> ~/.zshrc
  2. Reload your shell configuration:
  $source ~/.zshrc
  3. Verify Qt5 qmake:
  $qmake -v
  (Should show a Qt 5.x version)
​
Configure GSL and FFTW paths (recommended)
  0. $echo 'export GSL_PREFIX="$(brew --prefix gsl)"' >> ~/.zshrc
  $echo 'export FFTW_PREFIX="$(brew --prefix fftw)"' >> ~/.zshrc
  $echo 'export CPPFLAGS="-I${GSL_PREFIX}/include -I${FFTW_PREFIX}/include ${CPPFLAGS}"' >> ~/.zshrc
  $echo 'export LDFLAGS="-L${GSL_PREFIX}/lib -L${FFTW_PREFIX}/lib ${LDFLAGS}"' >> ~/.zshrc
  $echo 'export LIBRARY_PATH="${GSL_PREFIX}/lib:${FFTW_PREFIX}/lib:${LIBRARY_PATH}"' >> ~/.zshrc
  1. Reload your shell configuration:
  $source ~/.zshrc

Download and install SequenceTree4
  0. $cd ~
  1. $git clone https://github.com/btdvu/sequencetree4.git
  2. $cd sequencetree4/src
  3. $qmake
  4. $make
  5. $cd ..
  6. $mkdir tmp

  Run SequenceTree4
  0. $cd ~/sequencetree4/bin
  1. (macOS app bundle – recommended so sequences compile correctly)
  $chmod +x st4.app/Contents/MacOS/st4
  $./st4.app/Contents/MacOS/st4
  OR
  $open st4.app

