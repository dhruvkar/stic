## stic: a hackable static site generator script

### Warning: This is the first release and it's ugly but works. Use at your own risk.


**Why, Why, Oh Why another static site generator?**

I built this partly to learn, and partly because I didn't know what type of site I wanted. 
I wanted to be able modify the generator as my needs changed and didn't want to install then keep modifying a package. 
A script fit the bill.

**What it does**

stic does three things:

1. Generates a folder structure, if it doesn't exist already (see below). If you don't have one of the folders below, it'll generate it, otherwise leave will leave the folder structure alone.

```
-public
-assets
-templates
-articles
```

2. Converts all .md files in the *articles* folder to HTML using a template in *templates* folder.
3. Move all converted HTML files, and copy everything from the assets folder to the *public* folder.


**Dependencies**

1. Python 2.7+
1. python-markdown
1. jinja2


**Getting Started**

1. Install dependencies `pip install markdown jinja2`
2. Copy `stic.py` to the root folder of your site. i.e. right alongside the *public, assets, templates, articles* folders shown above.
3. Make it executable `chmod +x stic.py`
4. Run it `./stic.py -t`


**Other Options**

See all options by:

`./stic.py -h`
