from os import walk

def readFolder(mypath):
  files = []
  for (dirpath, dirnames, filenames) in walk(mypath):
      # filter hidden files
      files = [f for f in filenames if not f[0] == '.']
      break
  return files

if __name__ == "__main__":
    print(readFolder('./'))