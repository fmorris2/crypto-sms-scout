# Crypto SMS Scout

## Overview
The Crypto SMS Scout serves as a notification system for "upcoming" crypto currencies that may be worth purchasing. It scrapes
[coinmarketcap](https://coinmarketcap.com/) (via a RESTful API endpoint) for coin info, taking into account overall market cap, as well as the social media presence of
the coin's official Twitter account. If a coin is encountered which meets the specified criteria (< max market cap & >= minimum tweets in a week),
it will send a SMS message with the coin info to a list of phone numbers. Scouted coins are marked down in a file in the /data directory, so they
will not be considered again in the future.

## Future Improvements
Instead of having hard-coded constant values for prospective coin criteria, they should be loaded through either a config file, or even command
line arguments.

Criteria should be expanded so that the system is more intelligent. Market cap & Tweet volume makes for a very rudimentary filter.

## Python Dependencies
- [requests](http://docs.python-requests.org/en/master/)
- [lxml](http://lxml.de/)
- [twilio](https://www.twilio.com/docs/libraries/python)
- [twitter](https://pypi.python.org/pypi/python-twitter)

## Usage
1. Create a file named mobile_numbers in the data/ directory. Put each phone number on a new line. Example:
   - ```
     +14445556666
     +15556667777
     ```
2. Create a file named twilio_credentials in the data/ directory. The file should be in this format:
   - ```
     Twilio Account SID
     Twilio Auth Token
     ```
3. Create a file named keys in the data/ directory. This file will hold keys to access the [Twitter API](https://developer.twitter.com/en/docs/basics/authentication/overview/application-only). The file should be in this format:
   - ```
     consumer_key
     consumer_secret
     access_token_key
     access_token_secret
     ```
4. Run the program! On Unix-based systems, you can run this command:
   - ```
     nohup python main.py &
     ```
