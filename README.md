Repo for duksctf.github.io blog.

# Guideline to install jekyll and play locally before pushing stuff

Clone the actual repo with "git clone git@github.com:duksctf/duksctf.github.io.git"

Create a ```Gemfile``` with:

```
source 'https://rubygems.org'

require 'json'
require 'open-uri'
versions = JSON.parse(open('https://pages.github.com/versions.json').read)

gem 'github-pages', versions['github-pages']
```

For ubuntu:

```bash
sudo apt-get update
sudo apt-get install ruby2.0 rubygems
```
Install bundler:

```bash
gem install bundler
```

then do a ```bundle install```

To render your jekyll (do this in the repository you cloned):

```bash
bundle exec jekyll serve```

output if everything is working correctly:

```bash
-> $ bundle exec jekyll serve                                                 
Configuration file: /home/mofo/works/project/jekyll_blog/duksctf.github.io/_config.yml
            Source: /home/mofo/works/project/jekyll_blog/duksctf.github.io
       Destination: /home/mofo/works/project/jekyll_blog/duksctf.github.io/_site
 Incremental build: disabled. Enable with --incremental
      Generating... 
                    done in 0.382 seconds.
 Auto-regeneration: enabled for '/home/mofo/works/project/jekyll_blog/duksctf.github.io'
Configuration file: /home/mofo/works/project/jekyll_blog/duksctf.github.io/_config.yml
    Server address: http://127.0.0.1:4000/
  Server running... press ctrl-c to stop.

```

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
