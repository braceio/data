
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

Brace Data is a tool made by Brace.io. To contact us send an email to team@brace.io.
