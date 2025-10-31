import argparse

def _argparse():
    # print('parsing args...')
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-main_dir",type=str, default='', help="parent directory that store dataset")
    arg = parser.parse_args()
    return arg

def add(**kwargs):
    tmp_txt = str([i for i in list(kwargs.keys())])
    print(kwargs['args'].dir)
    print(f"{tmp_txt}, type: {type(tmp_txt)}")

def main():
    args = _argparse()
    print(args.dir)
    add(args=args, test=1)

if __name__=="__main__":
    main()