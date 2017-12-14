from bs4 import BeautifulSoup
import urllib
import codecs
import sys

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)


# python earthwise_scrapper.py


class ReadData:
    def get_country_list(self, url):
        country_list = []
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)
        dl_data = soup.find_all('dl')
        for dlitem in dl_data:
            dd_data = dlitem.find_all('dd')
            for dditem in dd_data:
                a = dditem.find('a')
                country = a['href']
                country_list.append(country)
        return country_list

    def scrapper(self, url):
        scrapper = {}
        authors = {}
        rdf_link = []
        cont = 0
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)
        description = soup.title.string
        rdf_link = [link["href"] for link in soup.findAll("link")
                    if "ExportRDF" in link.get("rel", [])]
        location = soup.find(
                   id="firstHeading").text.replace("Hydrogeology of ", '')
        url_resource = url
        index = url.rfind("/") + 1
        id = url[index:]

        mark = soup.find(id="Authors")
        if not mark:
            mark = soup.find(id="Compilers")
        if not mark:
            mark = soup.find(id="Contributers")
        for elt in mark.parent.nextSiblingGenerator():
            if elt.name == "h2":
                break
            if hasattr(elt, "text"):
                if elt.findChildren('b'):
                    raw = [a.string for a in elt.findAll(text=True)]
                    name = [b.string for b in elt.findAll('b')]
                    inst = list(set(raw) - set(name))
                    inst_name = [item for item in inst]
                    if ', ' in inst_name:
                        inst_name.remove(', ')
                    if ' and ' in inst_name:
                        inst_name.remove(' and ')
                    inst_value = []
                    for elem in inst_name:
                        if elem.startswith(', '):
                            new = elem[2:]
                            inst_value.append(new)
                        else:
                            inst_value.append(elem)
                    for elem in name:
                        authors[elem] = inst_value
                else:
                    if cont == 0:
                        citation = elt.text
                        cont += 1
                    else:
                        biblio_reference = elt.text
                        if biblio_reference.find("Accessed"):
                            biblio = biblio_reference.split("Accessed")[0]
                        else:
                            biblio = biblio_reference
                if cont == 1:
                    if citation.find("Accessed"):
                        biblio = citation.split("Accessed")[0]
                    else:
                        biblio = citation
        mark = soup.find(id="Terms_and_conditions")
        for elt in mark.parent.nextSiblingGenerator():
            if elt.name == "h2":
                break
            if hasattr(elt, "text"):
                if elt.findChildren('a'):
                    link = elt.find('a')
                    terms_of_use = link['href']

	scrapper['id'] = id 
        scrapper['url_resource'] = url_resource
        scrapper['authors'] = authors
        scrapper['description'] = description
        scrapper['rdf_link'] = rdf_link
        scrapper['location'] = location
        scrapper['biblio'] = biblio
        scrapper['terms_of_use'] = terms_of_use
        return scrapper


class WriteData:
    def print_values(self, scrapper):
        print("Resource: %s \n" % scrapper['url_resource'])
        print("Description: %s \n" % scrapper['description'])
        print("Location: %s \n" % scrapper['location'])
        for name in scrapper['authors']:
            print("Aut .%s - Inst:%s \n" % (name.encode('utf-8'), scrapper['authors'][name][0].encode('utf-8')))
        print ("Citation: %s \n" % scrapper['biblio'].encode('utf-8'))
        print ("Terms of use: %s \n" % scrapper['terms_of_use'])

    def export_rdf(self, scrapper):
        export_url = 'https://w3id.org/mint' 
        dataset = export_url + '/Dataset/' 
        catalog = export_url + '/Catalog/BgsCatalog' 
        idCatalog = "<" + catalog + ">"
        idRecurso = "<" + dataset + scrapper['id']+ ">"
        # we will have to describe in the future the URI
        # the distribution might be the dataset as well

        tripletas = idCatalog + " <http://www.w3.org/ns/dcat#dataset> " + " " + idRecurso + " .\n"
        tripletas += idRecurso + " a <http://www.w3.org/ns/dcat#Dataset>; \n"
        tripletas += "    <http://purl.org/dc/terms/publisher> <" + export_url + "/Agent/BGS>; \n"
        tripletas += "    <http://purl.org/dc/terms/spatial> \"" + scrapper['location'] + "\";\n"
        tripletas += "    <http://purl.org/dc/terms/description> \"" + scrapper['description'] + "\";\n"
        tripletas += "    <http://www.w3.org/ns/dcat#landingPage> <" + scrapper['url_resource'] + ">;\n"
        tripletas += "    <http://purl.org/dc/terms/bibliographicCitation> \"" + scrapper['biblio']+ "\";\n"
        tripletas += "    <http://purl.org/dc/terms/rigths> \"" + scrapper['terms_of_use'] + "\".\n"
 
        #tripletas_authors = URI per author - PERSONA, INSTITUTION

        print("%s \n" % tripletas)
    	

if __name__ == '__main__':

    rd = ReadData()
    wr = WriteData()
    url = "http://earthwise.bgs.ac.uk/index.php/Hydrogeology_by_country"
    country_list = rd.get_country_list(url)
    for url_country in country_list:
        #print (" ###### Extracting automaticaly: %s ###### \n" % url_country)
        extract_information = rd.scrapper(url_country)
        #wr.print_values(extract_information)
        wr.export_rdf(extract_information)
