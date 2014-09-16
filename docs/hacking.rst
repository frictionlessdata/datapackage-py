Hacking on datapackage
======================

Helping out with the development of **datapackage** is much appreciated
and we try to be a newcomer friendly project! There's a lot to do if we
are supposed to be the goto python package for working with `data
packages <http://www.dataprotocols.org/en/latest/data-packages.html>`__.

We don't track an awful lot except for perhaps bugs and feature requests
from non-developers (or very busy developers) in our issue tracker so
the development is mostly fueled by the *scratch your own itch* mantra.

So start off by looking at what `data
packages <http://www.dataprotocols.org/en/latest/data-packages.html>`__
can do and what feature you would like to see and use. Then just
implement it!

Development environment
-----------------------

We recommend using a
`virtualenv <http://virtualenv.readthedocs.org/en/latest/>`__ to set up
the environment. If you have it installed it's as simple as typing this
into a terminal:

::

    > virtualenv venv
    ... some stuff happens ...
    > source venv/bin/activate

There are other ways of doing this so feel free to read up on virtualenv
and choose your preferred method.

After setting up your work environment you need to install the
development requirements. That's easy to do with pip:

::

    > pip install -r requirements.dev.txt

Now you're ready to do some coding!

Development process
-------------------

All development now takes place in the *development* branch of our git
repository while master holds whatever is the most recent version of the
python package. This means that if you decide to hack on datapackage and
add something awesome to it (and just to clarify: `Everything is
Awesome! <http://en.wikipedia.org/wiki/Everything_Is_Awesome>`__) then
fork the repository, do your changes (if you intend on doing many
changes we recommend doing that in feature branches) and then create a
pull request against the development branch.

Fairly often when the development branch is regarded as feature complete
by some person with two much power it is merged into master, the version
is updated accordingly and the new package is uploaded to pypi. We try
to do this as often as possible so you can expect to see your code
released soon after you finish it.

I've coded some stuff, now what?
--------------------------------

At the moment we don't put any big restrictions on how you do your
development and what you need to do, but there are two things we
strongly recommend:

1. If you've added any features, create tests for your code (in the
   tests directory). This will help us maintain that feature in the
   future. Also, be sure you haven't broken anything by running the
   tests. That's as easy as typing ``nosetests`` in the commandline.
2. Try to be polite and helpful. We do that by creating maintainable and
   newcomer friendly code. More comments are better than too few
   comments so err on the Sherlock-commenting side (comments where the
   reader goes: "No shit Sherlock!"). Also conform to the pep8 style
   guide and don't include unnecessary code. We've included a
   development requirement for a tool that helps you out. It's called
   `flake8 <https://flake8.readthedocs.org/en/latest/>`__ and all you
   have to do is make sure running this in the commandline:
   ``flake8 datapackage`` doesn't produce any output.

Dont' forget to add yourself to the CONTRIBUTORS file when you've
contributed something.

Oh... and also. The team (we who are interested in developing this
python package so you can be a part of the team right now if you want)
is a very happy team so don't forget to remind people in comments and
pull requests how happy you are about things. Programming is fun so
don't forget to share the joy of programming with all of us!
