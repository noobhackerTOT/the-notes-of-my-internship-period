The id Command

When you run the command id in your terminal, it acts like a digital ID
card scanner for your Linux user account.

What it does: It pulls data from the system to show you exactly who you
are logged in as and what \"permissions\" you have based on the groups
you belong to.

Why it\'s important: In Linux, \"User Information\" determines what
files you can open, edit, or delete, and what programs you can run. By
knowing your uid (User ID) and the groups you belong to, you can
understand why you might be allowed to run some commands (like those
requiring sudo) and why others might be restricted.

How the logic works:

Request: By typing id, you are requesting the system to look through its
security records.

Lookup: The system finds your username (labex) and checks its internal
database for all associated IDs and group memberships.

Display: It prints that summary to your terminal so you can verify your
status.

**Home directory（主目录）** 和 **working
directory（工作目录）** 是操作系统中两个不同用途的目录概念：

  ------------------------------------------------------------------------------------------------------------------------------------------
  特性             Home Directory                                               Working Directory
  ---------------- ------------------------------------------------------------ ------------------------------------------------------------
  **定义**         用户登录后拥有的专属目录，通常用于存放个人文件、配置文件等   当前进程（如终端、应用程序）所在的目录位置

  **归属**         每个用户一个固定的主目录                                     每个进程有自己的工作目录，可以随时改变

  **典型路径**     Unix/Linux：/home/用户名\                                    例如 /home/用户名/Documents 或 C:\\项目
                   Windows：C:\\Users\\用户名                                   

  **如何查看**     echo \$HOME（Linux/macOS）\                                  pwd（Linux/macOS）\
                   %USERPROFILE%（Windows）                                     cd（Windows 无参数）

  **改变方式**     一般不会改变（除非修改账户配置）                             使用 cd 命令随时切换

  **常见用途**     保存个人配置（.bashrc）、文档、桌面、下载等                  执行命令时的相对路径基准，比如 ls 会列出当前工作目录的内容
  ------------------------------------------------------------------------------------------------------------------------------------------

在linux文件夹系统下，在文件前面加.可以实现隐藏对应的文件

ls -a 可以显示所有文件 包括隐藏的文件夹

-r代表递归的处理 代表不止处理最上面一层 还会处理其子层
