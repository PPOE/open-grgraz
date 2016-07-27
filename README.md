open-grgraz
===========

a script to parse the [City Council of Graz](http://www.graz.at/cms/beitrag/10193600/4519286)
(Gemeinderat Graz) [Microsoft SharePoint](https://en.wikipedia.org/wiki/SharePoint)
for motions and answers.

 - Author: Peter Grassberger <petertheone@gmail.com>
 - License: [MIT](https://opensource.org/licenses/MIT)

![open-grgraz downloading](https://raw.github.com/PPOE/open-grgraz/master/open-grgraz.jpg "open-grgraz downloading (c) @stefan2904")

Thanks to
---------

- [mattgwwalker/msg-extractor](https://github.com/mattgwwalker/msg-extractor)
- [@stefan2904](https://github.com/stefan2904)

script stages
-------------

1. Login/Authentication (wip)
2. Download json motion lists to `files/jsonMotionLists` folder (wip)
3. Parse json files create `motions.csv`
4. Download files from `motions.csv`
5. Parse Emails and download/extract more files


run
---

run django with `sudo python3.4 manage.py runserver`.
