# fix-bind

Purpose of this code: default linux mount doesn't checks if binded mount became broken.
It can happen when mounted dir was removed and created again: bind is based on inode numbers,
that will be changed for recreated dir, and bind will break silently.
One should find and remount all bind mounts because of this.
Script is reading content from /etc/mtab and for every mount with bind method checks that inodes
of mounted dir and mount point are the same.
If they're not, it does umount and mount dirs again.
