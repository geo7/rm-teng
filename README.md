# rm-teng

An attempt to minimise the impact of `rm` in careless hands. Note, minimise,
not prevent.

## Motivation

A couple of times I've managed to `rm -rf {{ some-dir }}` accidentally and,
each time, it's been _verrry_ annoying. Having something which stored `{{
some-dir }}` in a different location would have enabled me to undo the error.
Issue here is `rm -i` wouldn't have saved me, I've deleted things _thinking_
they were safe to delete then found out they weren't.

## Usage

### Basic

Expected usage is as follows:

```sh
# in .zshrc / .bashrc / .whatever
alias rm="uvx rm-teng"
```

The only case that's currently handled is `rm -rf {{ some-dir }}`.

### Configuration

Configuration is done via the following env vars:

- `RM_TENG_DELETION_DIR`: Optional, controls where to store files that are relocated by `rm-teng`. If set it must be an absolute path. Default is `~/.rm_rf_files`.
- `RM_TENG_DOUBLE_CHECK`: Optional, controls whether to prompt for confirmation when running `rm` commands that don't have any handlers set. Default is `false`.

### What it doesn't do

If used in the way outlined above `rm-teng` is only called when called
_interactively_ from the shell. It won't be called from scripts, and it won't
be called from something like `find . -type f | xargs rm` (see
https://zsh.sourceforge.io/Doc/Release/Shell-Grammar.html#Aliasing or similar
if unfamiliar).

### Cleaning up

When `rm -rf {{ some-dir }}` is run the directory is moved to `~/.rm_rf_files`
instead of being deleted. As a result a few entries can build up here.

`rm-teng` doesn't currently handle cleaning these up. It's pretty easy to do
something along the lines of:

```sh
# Simple workflow to check what is in the {{ deleted-dir }} older than a certain
# time, and delete.

# check what's there
find . -mindepth 1 -type d -ctime +10 | less
# delete (if ok)
find . -mindepth 1 -maxdepth 1 -type d -ctime +10 -print0 | xargs -0 rm -rf
```

Hopefully a bit more mindfulness can be applied at this stage!

### Restore deleted

Alternatively, you should be able to restore something by simply moving it back
where it was.

E.g: if we have `~/one/two/three/four/five`, then run `rm -rf one` it'll create:

```
{{ timestamp }}
└── Users
  └── user_name
    └── one
      └── two
        └── three
          └── four
            └── five
```

Then from `~/` you can run `mv {{ rm-teng-dir }}/{{ timestamp }}/Users/user_name/one ./` to restore.

## Alternative solutions

I've managed to find more of these after writing most of this, you might find one more suitable! `rip2` and `rm-protection` (who I copied most of this list off) look nice, though I've not really used either:

- https://github.com/Byron/trash-rs
- https://github.com/MilesCranmer/rip2
- https://github.com/alanzchen/rm-protection
- https://github.com/andreafrancia/trash-cli
- https://github.com/hitzhangjie/rm
- https://github.com/kaelzhang/shell-safe-rm (bash)

## Future development

I've had this running for a bit and have found it fine. Adding additional handlers should be pretty straightforward, it would also be easy to implement custom handlers for user specific settings.
