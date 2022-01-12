
![AutoFarm](doc/res/Autofarm-Logo.png)

### Easy dynamic process invocation rewriting and offloading to other machines.

[![Python package](https://github.com/Vinpasso/autofarm/actions/workflows/python-package.yml/badge.svg)](https://github.com/Vinpasso/autofarm/actions/workflows/python-package.yml)
[![CMake](https://github.com/Vinpasso/autofarm/actions/workflows/cmake.yml/badge.svg)](https://github.com/Vinpasso/autofarm/actions/workflows/cmake.yml)

Ever wanted to distribute processes to other machines without going through the trouble of changing an application or build system? 
Ever wish that a program or script could just be fixed to call the correct executable or swap out some arguments?
You can now do these things in no time with AutoFarm!

## Easy Multi-Node Distributed Builds

Do you build things? Like a lot? Surely you spend a lot of time waiting for build processes to complete. 
Perhaps you even have an entire supercomputer at your disposal but are sitting on the login node waiting for compilation to finish? 
No more! 
AutoFarm can distribute your compiler invocations for you automatically. You just need a parallelizable build process 
(you already have this if you can run `make -j 4`), working password-less `ssh` to your other build machines, 
and a shared file system on your cluster for shared build output.

Then your build process can be modified from a boring old single-system parallel build:

```shell
$ > make -j 8
```

to become a havoc-wreaking monster of a build:

```shell
$ > autofarm ssh --hosts buildserver[0-10] run make -j $((10*8))
```

Neat! How fast is it?

## Swap Commands or Arguments

Have a system that wants to run a command, but it doesn't work because the invocation is not quite right? 
Don't have the ability to change that invocation first hand? AutoFarm to the rescue. 
AutoFarm allows you to simply rewrite process invocations without fiddling with the application or your system.

Perhaps you have a badly written build file that wants to call `gcc` all the time, but you only have `clang`:

```bash
$ > autofarm rewrite --replace 'gcc' 'clang' run make
```

Maybe your application or script was written for `avconv`, but you only have `ffmpeg`:

```bash
$ > autofarm rewrite --replace 'avconv' 'ffmpeg' run ./convert_videos.sh
```

Or maybe you want to prevent the application from doing something stupid and just want to see the commands it would have run?

```shell
$ > autofarm rewrite --replace '^' 'echo' run make
```

AutoFarm can rewrite almost any process invocation, and you can even write the logic yourself. See the documentation.

## Installation

AutoFarm is available via `pip`. You can easily install it by running:

```shell
$ > pip install autofarm
```

If you are running on Linux, pip should install the necessary binary libraries automatically. 
If for some reason you need to compile from scratch because there isn't a binary distribution for your system, 
then CMake as well as a C++ compiler and a working internet connection are required. 

## How it works

AutoFarm uses the `LD_PRELOAD` mechanism to intercept the `exec` family of functions 
(see the relevant [man page](https://linux.die.net/man/3/exec)) of `libc`. While there are some exceptions 
(such as programs written in go), a great majority of programs use this mechanism to spawn new processes. 
Once AutoFarm intercepted your program trying to call `exec`, it can arbitrarily modify the invocation. 
That means it can change the program, any arguments, or the environment to its heart's content.
