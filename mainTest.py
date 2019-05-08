link = 'https://hlj.com/media/catalog/product/cache/image/e9c3970ab036de70892d86c6d221abfe/b/a/bans57842_3.jpg'

filename = link.rsplit('/', 1)[-1]

dirname = filename.rsplit('_', 1)[0]

print(filename, dirname)