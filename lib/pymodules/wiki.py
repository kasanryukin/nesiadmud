import requests, mud, mudsys, textwrap, json, re
from bs4 import BeautifulSoup
from lxml import html
from urllib.parse import quote

book_name = 'wikipedia_en_top_nopic'

# tools for looking something up using the search api
base_url = 'http://192.168.0.80:8040/content/' + book_name + '/A/'
search_url_prefix = "http://192.168.0.80:8040/search?pattern="
search_url_suffix = "&books.name=" + book_name

# tools for looking something up using the suggest api
# curl 'http://localhost/suggest?content=stackoverflow_en&term=pyth&count=50'

suggest_url = 'http://192.168.0.80:8040/suggest?content=' + book_name + '&' + 'term='

def remove_tags(text):
    """Remove square bracket tags of the form [lower-alpha #] and [#] and their contents from the text."""
    return re.sub(r'\[(?:lower-alpha \d+|\d+)\]', '', text)

def remove_styles(text):
    """Remove CSS styles from the text."""
    # Define a regular expression pattern to match CSS styles
    pattern = r'\.mw-parser-output \..*?\{.*?\}'
    # Remove the styles using re.sub
    cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
    return cleaned_text



def do_suggest(arg, count=3):
    full_url = suggest_url + quote(arg)
    response = requests.get(full_url + "&count=%d" % (count))
    return response.text

def do_search(arg, pageLength=10):

    full_url = search_url_prefix + quote(arg) + search_url_suffix
    response = requests.get(full_url + "&pageLength=%d" % (pageLength))
    return response.text

def do_lookup2(url):

    response = requests.get(url)

    if response.status_code == 200:
        # Parse the HTML content using lxml
        tree = html.fromstring(response.content)

        # Find the first 'p' element
        first_paragraph = tree.find('.//p')
        # Print the text content of the first 'p' element
        if first_paragraph is not None:
            retval = html.tostring(first_paragraph, method='text', encoding='unicode').strip()
            retval = remove_tags(retval)
            retval = remove_styles(retval)
            return textwrap.fill(retval, width=80)
        else:
            return "No 'p' element found."
    else:
        return 'Error:' + str(response.status_code)


def cmd_wsearch(ch, cmd, arg):
    ch.send(do_search(arg, 2).encode('utf-8'))

'''def cmd_wsuggest(ch, cmd,arg):
    ch.send(do_suggest(arg, 3).encode('utf-8'))'''

def cmd_wiki(ch, cmd, arg):

    if not arg:
        ch.send("Look up what?")
        return

    json_data = do_suggest(arg, 3)
    data = json.loads(json_data)
    path_values = [item['path'] for item in data if 'path' in item]

    if len(path_values):
        # ch.send(str(path_values))
        # ch.send(str(data))
        url = 'http://192.168.0.80:8040/content/' + book_name + "/" + path_values[0]
        # ch.send("url: " + url)
        retval = do_lookup2(url)
        if retval.startswith("Error:404"):
            ch.send("We couldn't figure out what you were after.")
        else:
            ch.send(do_lookup2(url))
        return
    else:
        ch.send("We couldn't figure out what you were after.")

    # url = 'http://192.168.0.80:8040/content/wikipedia_en_top_nopic/A/' + arg
    # ch.send(do_lookup2(url).encode('utf-8'))

mudsys.add_cmd("wiki",   None, cmd_wiki,   "player", True)
# mudsys.add_cmd("wsearch", None, cmd_wsearch,  "player", True)
# mudsys.add_cmd("wsuggest", None, cmd_wsuggest, "player", True)
