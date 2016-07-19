open-grgraz
===========

a script to parse the [City Council of Graz](http://www.graz.at/cms/beitrag/10193600/4519286)
(Gemeinderat Graz) [Microsoft SharePoint](https://en.wikipedia.org/wiki/SharePoint)
for motions and answers.

script stages
-------------

1. Login/Authentication (wip)
2. Download json motion lists to `files/jsonMotionLists` folder (wip)
3. Parse json files create `motions.csv`
4. Download files from `motions.csv`
5. Parse Emails and download/extract more files
