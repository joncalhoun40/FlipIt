You can obtain the Sources or the Pre-Built Binaries of LLVM and Clang from [here](http://llvm.org/releases/download.html).

Installing LLVM and Clang from Pre-Built Binaries saves your time and trouble of directly compiling the Sources by yourself. You can follow the instruction [here](http://stackoverflow.com/questions/17045954/how-to-install-clang-using-precompiled-binaries) and [here](http://askubuntu.com/questions/89615/how-do-i-install-llvm-clang-3-0) to learn more about how to install the binaries.

You can also install LLVM and Clang from the Sources, please check [here](http://llvm.org/docs/GettingStarted.html#requirements) for the requirements of building LLVM by yourself. If you are using Ubuntu or Debian, it is probably a good idea to install the `build-essential` package before you start, since it contains the required `gcc` and `make` utilities. After all the requirements are met, click [here](http://llvm.org/docs/GettingStarted.html#getting-started-with-llvm) for a very detailed instruction and some options you can configure when installing LLVM. 
Please do note the following when you follow the instructions above:
1.	The linking process of LLVM is very memory heavy, make sure your machine has enough memory and swap space before you compile LLVM Source Code. Otherwise you risk the chances of getting errors like `ld terminated with signal 9`, `Memory exhausted` or `ld returned exist status 1` which halts and fails the compilation process. Some helpful links on how to increase swap space can be found [here](https://www.maketecheasier.com/swap-partitions-on-linux/), [here](https://blog.inventic.eu/2012/07/linux-c-linker-ld-terminated-with-signal-9/) and [here](http://stackoverflow.com/questions/5682854/why-is-the-linker-terminating-on-me-when-i-build-clang).
2.	You can also choose to build LLVM in Release mode instead of Debug mode to reduce the amount of memory required during compilation. See [here](http://llvm.org/docs/GettingStarted.html#local-llvm-configuration) and [here](http://llvm.org/docs/CMake.html#introduction) about how to change local LLVM configuration. 
3.	Instructions on installing LLVM and Clang without Root Privileges can be found [here](http://stackoverflow.com/questions/8681385/install-clang-as-user-no-root-privileges) and [here](http://llvm.org/docs/GettingStarted.html#local-llvm-configuration).