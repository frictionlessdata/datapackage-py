# Hacking on datapackage

Helping out with the development of **datapackage** is much appreciated
and we try to be a newcomer friendly project! There's a lot to do if we
are supposed to be the goto python package for working with [data
packages](http://www.dataprotocols.org/en/latest/data-packages.html).

We don't track an awful lot except for perhaps bugs and feature requests
from non-developers (or very busy developers) in our issue tracker so
the development is mostly fueled by the *scratch your own itch* mantra.

So start off by looking at what [data
packages](http://www.dataprotocols.org/en/latest/data-packages.html) can
do and what feature you would like to see and use. Then just implement
it!

## Development environment

We recommend using a
[virtualenv](http://virtualenv.readthedocs.org/en/latest/) to set up the
environment. If you have it installed it's as simple as typing this into
a terminal:

    > virtualenv venv
    ... some stuff happens ...
    > source venv/bin/activate

There are other ways of doing this so feel free to read up on virtualenv
and choose your preferred method.

After setting up your work environment you need to install the
requirements. That's easy to do with pip:

    > pip install -e .

Let's run the tests to be sure everything is working. We need to install
**tox** if you don't have it already. To do so, run:

    > pip install tox

Then simply run:

    > tox

The tests will run and, after a while, you should see the result. If
everything is green, you're ready to do some coding!

## Development process

The development takes place in the *master* branch of our git
repository. If you decide to hack on datapackage and add something
awesome to it (and just to clarify: [Everything is
Awesome!](http://en.wikipedia.org/wiki/Everything_Is_Awesome)) then fork
the repository, do your changes (if you intend on doing many changes we
recommend doing that in feature branches) and then create a pull request
against the master branch.

## I've coded some stuff, now what?

At the moment we don't put any big restrictions on how you do your
development and what you need to do, but there are two things we
strongly recommend:

1.  If you've added any features, create tests for your code (in the
    tests directory). This will help us maintain that feature in the
    future. Also, be sure you haven't broken anything by running the
    tests. That's as easy as typing `nosetests` in the commandline.
2.  Try to be polite and helpful.
3.  Conform to the pep8 style guide and don't include unnecessary code.

Dont' forget to add yourself to the CONTRIBUTORS file when you've
contributed something.

Oh... and also. The team (we who are interested in developing this
python package so you can be a part of the team right now if you want)
is a very happy team so don't forget to remind people in comments and
pull requests how happy you are about things. Programming is fun so
don't forget to share the joy of programming with all of us!
