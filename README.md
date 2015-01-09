**NOTE:** This project is not being actively maintained. Please see the fork at [github.com/asm-products/gridspree](http://github.com/asm-products/gridspree) for further development, and join the discussion at [assembly.com/gridspree](http://assembly.com/gridspree).

DATA by Brace
-------------

Use Google Spreadsheets as your CMS. Display your spreadsheet data however you like right on your static site.


## How it works

Connect your Google Spreadsheet to Brace Data. Then you can use mustache templates to display your data, or post new data with a form.

#### Easily display spreadsheet data:

    <script src="https://data.brace.io/ss/READ_KEY.js"></script>

    <script type="x-brace-template">
      <ul>
        {{#rows}}
          <li>
            {{Price}},
            {{Title}}, 
            {{Quantity}}
          </li>
        {{/rows}}
      </ul>
    </script>

#### Post new entries:

    <form action="https://data.brace.io/ss/WRITE_KEY" method="POST">
        <input type="text" name="Price">
        <input type="text" name="Title">
        <input type="text" name="Quantity">
        <input type="submit" value="Send">
    </form>


## Some questions you might have:

#### Who are you guys?

We're the same folks who make Brace.io, the simple way to host websites. Brace Data is a side project that solves a problem many of Brace.io users seem to face: incorporating dynamic data into otherwise static HTML pages.

#### What about privacy?

We don't store the contents of your spreadsheet. Instead we generate two access keys that link our APIs to your spreadsheet, one for reading and one for writing. You can delete these keys at any time to revoke access.

#### How much does it cost?

Brace Data is free for 1000 API calls per spreadsheet each month. If you need more, please reach out.

#### Are there any limits?

Yep, for now we cap API calls to 1000 per spreadsheet for each month. If you need more, please reach out to team@brace.io.

--------

Running your own copy of Brace Data 
------------------------------------

### Running on localhost

You'll need python 2.7 and should [install pip](https://pip.pypa.io/en/latest/installing.html), and create a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for the server. 

Once your environment is setup, clone the source and cd into the root of the Brace Data repository. Then run:

    pip install -r requirements.txt

then

    python manage.py runserver


### Running on heroku

You will need to install the [heroku toolbelt](https://toolbelt.heroku.com/).

Once your environment is setup, clone the source and cd into the root of the Brace Data repository. Then run:

    heroku apps:create [your project name]

then

    git push heroku

Your new project will be running at [your project name].herokuapp.com.


### Dependencies

Brace Data requires Redis and MongoDB. If you're deploying to heroku you can get an addons, such as redistogo and mongohq. To install redistogo and mongohq into your project just run the commands:

    heroku addons:add redistogo
    heroku addons:add mongohq


Brace Data also requires a google developer credentials with the following APIs enabled:

    Google Cloud Storage JSON API
    Google+ API


### Configuring Brace Data

Take a look at the `main/settings.py` file for a list of environment variables that should be set in order for Data to work correctly.

