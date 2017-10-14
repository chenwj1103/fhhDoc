- 在dev的远程分支下创建一个分支
- git checkout -b issue1 origin/dev
- 开发...
- git add .
- git commit -m "test git rebase"

-- git log

```
commit afd45bdda666378dd50067b470fec18a3ab992d5 (HEAD -> issue2)
Author: 陈伟杰 <chenwj3@ifeng.com>
Date:   Tue Aug 1 23:30:30 2017 +0800

    test git rebase

commit b83b8bb7395360880484dfbf1f570e6a4770b91e (origin/master, origin/HEAD, master)
Author: 陈伟杰 <chenwj3@ifeng.com>
Date:   Tue Aug 1 23:25:48 2017 +0800

    性能测试调整

commit 6e5fe97d97109e743933a7a15b193afffffe91ef
Author: 陈伟杰 <chenwj3@ifeng.com>
Date:   Tue Aug 1 20:46:34 2017 +0800

    添加redis server等相关的命令

```

- 此时合并dev分支的最新的代码
- git pull --rebase

```
commit 675da3c27185cfd00efe3ba30a37a46dc8c17ab2 (HEAD -> issue2)
Author: 陈伟杰 <chenwj3@ifeng.com>
Date:   Tue Aug 1 23:30:30 2017 +0800

    test git rebase

commit 6416ac8b42b3b05918907677dc9cc2504db5a33f (origin/master, origin/HEAD, master)
Author: 陈伟杰 <chenwj3@ifeng.com>
Date:   Tue Aug 1 23:35:00 2017 +0800

    master update code

commit b83b8bb7395360880484dfbf1f570e6a4770b91e
Author: 陈伟杰 <chenwj3@ifeng.com>
Date:   Tue Aug 1 23:25:48 2017 +0800

    性能测试调整

commit 6e5fe97d97109e743933a7a15b193afffffe91ef
Author: 陈伟杰 <chenwj3@ifeng.com>
Date:   Tue Aug 1 20:46:34 2017 +0800

    添加redis server等相关的命令

```


- 有冲突解决冲突（此时rebase命令会中断，解决冲突后执行此命令）
- git rebase --continue

- 如果你想跳过该patch
- git rebase --skip

- 如果你想放弃rebase该分支
- git rebase --abort


- 关联被追踪的远端分支
- git branch --set-upstream-to=origin/<branch>  your-local-branch


- 查看追踪的远端分支
- git branch -vv