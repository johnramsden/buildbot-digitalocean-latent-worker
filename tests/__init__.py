# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import DigitalOceanLatentWorker

def create_worker():
    print("Creating test worker")

def main():
    create_worker()

if __name__ == "__main__":
    # execute only if run as a script
    main()