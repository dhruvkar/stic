## stic: a hackable static site generator script

##### Warning: This is the first release. It's ugly, but it works. Use at your own risk.

___

### Why, Why, Oh Why another static site generator?

I built this partly to learn, and partly because I didn't know what type of site I wanted. 

I wanted to be able modify the generator as my needs changed and didn't want to install then keep modifying a package. 

A script fit the bill.

____

### What it does

stic does three things:

* Generates a folder structure, if it doesn't exist already. If you don't have any of folders below, it'll generate it, otherwise leave will leave the folder structure unaltered.

```
-public
-assets
-templates
-articles
```

* Converts all .md files in the *articles* folder to HTML using a template in *templates* folder.
* Move all converted HTML files, and copy everything from the *assets* folder to the *public* folder.

____

### Dependencies

1. Python 2.7+
1. python-markdown
1. jinja2

____

### Getting Started

1. Install dependencies: `pip install markdown jinja2`
2. Copy `stic.py` to the root folder of your site. i.e. right alongside the *public, assets, templates, articles* folders.
3. Make it executable: `chmod +x stic`
4. Run it: `./stic -t`

____

### Rules and Options

See all options by:

`./stic -h`


All markdown files to be converted need to have the extension **.md**

All templates use jinja and need to have the extension **.jinja2**
