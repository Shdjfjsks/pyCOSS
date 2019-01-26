## Overview

pyCOSS is an attempt to clear up COSS.io's exchange API to make it clearer and more intuitive for developers to use for developing trading bots on the exchange. It is also intended to allow for developers to use these functions as a template for their own implementations of the API in other languages.

To instantiate the client:

from pyCOSS import PyCOSSClient

client = PyCOSSClient(api_public='your_public_key', api_secret='your_secret_key')

You can then call all methods associated with the COSS web API.
