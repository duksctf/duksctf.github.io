# Guideline to post a new Writeup:

1. clone the actual repo with "git clone git@github.com:duksctf/duksctf.github.io.git"
2. in the _posts directory copy the template available under _drafts/xxxx-xx-xx-CTFYEAR-name-of-the-task.md.
3. Edit the template at your convenience, don't change the layout and the
   title, rename it with 2016-MM-DD-CTFYEAR-name-of-the-task.md 
4. For Markdown syntax, you can check [Markdown CheatSheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
5. When you think everything is ready, git checkout -b writeup-task
6. git add _posts/yournewwriteup.md
6. git add resources
7. git commit -m 'added writeup for CTF XXX task XXX'
8. git checkout master
9. git merge writeup-task
10. git push
