import requests
from bs4 import BeautifulSoup as bs


class SkClient:
    def __init__(self, login=None, password=None, url=None):
        '''
        :param:login - login do szkopula
        :param:passowrd - haslo do szkopula
        :param:url - link do strony glownej zajec na szkopule
        '''
        self.ids = []
        if login is not None:
            self.login = login
        if password is not None:
            self.password = password
        if url is not None:

            self.redirect_to = ''
            self.temp_url = ''
            self.redirecotr = ""
            22
            tamp_url = list(url)
            for i in range(len(tamp_url)):
                if (i < 22):
                    self.temp_url += tamp_url[i]
                else:
                    if (i < len(tamp_url) - 2):
                        self.redirecotr += tamp_url[i]
                    self.redirect_to += tamp_url[i]
            self.submitions_url = f"{self.temp_url}{self.redirecotr}account/login/?next={self.redirecotr}submissions/"
            self.url = f"{self.temp_url}{self.redirecotr}account/login/?next={self.redirect_to}"
            self.task_url = f'{self.temp_url}{self.redirecotr}'
            self.base_url = self.temp_url
            self.check_url = f"{self.temp_url}{self.redirecotr}submissions/"
            self.ranked = f"{self.temp_url}{self.redirecotr}account/login/?next={self.redirecotr}ranking/"
            "https://szkopul.edu.pl/c/cslom/account/login/?next=/c/cslom/p/"
            "https://szkopul.edu.pl/c/cslom/p/"

    def Login(self):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "referer": self.url
        }

        rq = requests.session()
        rq.headers.update(headers)

        token = rq.get(self.url)
        if token.status_code != 200:
            raise Exception("Error while getting token. Check your login and password.")

        if 'csrftoken' in token.cookies:
            csrftoken = token.cookies['csrftoken']
        else:
            csrftoken = token.cookies['csrf']

        self.csrftoken = csrftoken
        self.session = rq

        return self

    def GetTasks(self, only_not_completed=False):
        '''

        :param only_not_completed: parametr ktory ustala czy chcemy otrzymac tylko niekompletne zadania czy wszystkie (false by deafult)
        :return: funkcja GetTasks zwraca tablice zadan gdzie kazede zadanie jest reprezentowane jako jedna tablica
        a indexy ida kolejno:
        0 - link do podgladu zadania
        1 - link do wyslania zadania
        2 - skrocona nazwa zadania
        3 - pelna nazwa zadania
        4 - ilosc prob
        5 - ilosc punktow zdobytych z zadania
        6 - ostatni warunek jest rowny "Wyslij" jezeli zadanie da sie odeslac
        '''

        rq = self.session

        payload = {
            "csrfmiddlewaretoken": f"{self.csrftoken}",
            "login_view-current_step": "auth",
            "auth-username": self.login,
            "auth-password": self.password

        }

        res = rq.post(url=self.url, data=payload)
        zupa = bs(res.content, features="html.parser")

        con = zupa.find('section', class_="col-lg-9 col-xl-10 main-content").find('tbody')

        links = []
        for i in con.find_all('tr', class_=None):
            pot = 0
            zad = []
            for j in i.find_all('td', class_="text-right"):
                for jj in j.find_all('a'):
                    if "submit" in jj['href']:
                        links.append(jj['href'])

        zadania = []
        poo = 0
        for i in con.find_all('tr', class_=None):
            pot = 0
            zad = []
            for j in i.find_all('td'):

                mom = j.text
                uou = ""

                if pot < 2:
                    for i in mom:
                        if i != '\n':
                            uou += i
                else:
                    for i in mom:
                        if i == 'z':
                            uou += '/'
                        elif i != '\n' and i != ' ':
                            uou += i

                if pot == 0:
                    link = f"{self.task_url}p/{uou.lower()}"
                    zad.append(link)
                    link = f"{self.base_url}{links[poo]}"
                    zad.append(link)
                zad.append(uou)

                pot += 1
            zadania.append(zad)
            poo += 1
        for i in range(len(zadania)):
            if zadania[i][5] == '':
                zadania[i][5] = 0
            else:
                zadania[i][5] = int(zadania[i][5])

        # rozdzialy
        if only_not_completed == True:
            o = []
            for i in zadania:
                if i[5] != 100:
                    o.append(i)
            return o
        else:
            return zadania

    def SendFile(self, link=None, plik=None, filetype=None):
        '''
        :param: link - link do wysłania zadania na szkopule (jeden z elementow zwrotu zadan)
        :param: plik - plik do wyslania
        :param: filetype - typ pliku do wyboru : C, C++ , Pascal , python

        :exception:Wszystkie parametry muszą byc uzupełnione aby modol zadzialal

        :return: zwraca status_code z wyslania pliku (wszystko wieksze rowne 400 oznacza ze cos nie dziala)
        '''

        if link != None and plik != None and filetype != None:

            idtofind = ""

            for i in link:
                try:
                    if (int(i) <= 9):
                        idtofind += i
                except:
                    None

            # print(idtofind)

            with open(plik, 'r') as f:
                p = f.read()
                f.close()

            rq = self.session

            payload = {
                "csrfmiddlewaretoken": f"{self.csrftoken}",
                "login_view-current_step": "auth",
                "auth-username": self.login,
                "auth-password": self.password

            }
            _ = rq.post(url=self.url, data=payload)
            token = rq.get(self.url)

            if 'csrftoken' in token.cookies:
                csrftoken = token.cookies['csrftoken']
            else:
                csrftoken = token.cookies['csrf']

            payload = {
                "csrfmiddlewaretoken": csrftoken,
                "problem_instance_id": idtofind,
                "file": "(binary)",
                "code": p,
                f"prog_lang_{idtofind}": f"{filetype}"
            }
            re_u = rq.post(url=link, data=payload)
            zupa = bs(re_u.content, features="html.parser")

            return re_u.status_code
        return 404

    def CheckLatest(self, all=False):
        '''

        :param all: jezeli jest ustawiony na true zamiast pokazywac ostatniego wyslanego pliku pokazuje wszystkie wyslane przez urzytkownika zadania
        :return: lista wyslanych zadan jezeli all == True. Jezeli nie wydaje najnowsze wyslane zadanie
        :returns: lista zadania jest zbudowana tak
        0 - data
        1 - link do podgladu
        2 - nazwa
        3 - ocena
        4 - ocena2
        5 - punkty
        :exception: warto zaznaczyc ze program jezeli zwraca liste zadan zwraca je w kolejnosci chronologicznej (czasowo)
        '''

        if all == False:

            rq = self.session
            payload = {
                "csrfmiddlewaretoken": f"{self.csrftoken}",
                "login_view-current_step": "auth",
                "auth-username": self.login,
                "auth-password": self.password

            }

            data = rq.post(url=self.submitions_url, data=payload)
            output = []
            o = ""
            serch_E = bs(data.content, features="html.parser")
            sekcja = \
            serch_E.find('section', class_="col-lg-9 col-xl-10 main-content").find('tbody', class_=None).find_all('tr',
                                                                                                                  class_=None)[
                0].find_all('td')  # [5].text

            gg = True
            for i in sekcja:
                l = i.find('a')
                if l is not None:
                    l = f"{self.base_url}{l.get('href')}"

                for j in i.text:
                    if (j != ' ' and j != '\n'):
                        o += j
                if (o == "Błądkompilacji"):
                    output.append(o)
                    output.append(0)
                if (o != '' and o != 'Szczegóły'):
                    output.append(o)
                if (l != None and gg != False):
                    output.append(l)
                    gg = False
                o = ""

            return output
        else:
            glob_output = []

            self.last = "0"

            def send(addditional=""):
                num = ""

                rq = self.session

                cookies = rq.get(f"{self.submitions_url}{addditional}")

                if 'csrftoken' in cookies.cookies:
                    csrftoken = cookies.cookies['csrftoken']
                else:
                    csrftoken = cookies.cookies['csrf']

                payload = {
                    "csrfmiddlewaretoken": f"{csrftoken}",
                    "login_view-current_step": "auth",
                    "auth-username": self.login,
                    "auth-password": self.password

                }

                data = rq.post(url=f"{self.submitions_url}{addditional}", data=payload)
                output = []
                o = ""
                serch_E = bs(data.content, features="html.parser")
                sekcja = serch_E.find('section', class_="col-lg-9 col-xl-10 main-content").find('tbody',
                                                                                                class_=None).find_all(
                    'tr', class_=None)  # [5].text

                for hh in sekcja:
                    gg = True
                    for i in hh.find_all('td'):
                        l = i.find('a')
                        if l is not None:
                            l = f"{self.base_url}{l.get('href')}"

                        for j in i.text:
                            if (j != ' ' and j != '\n'):
                                o += j
                        if (o == "Błądkompilacji"):
                            output.append(o)
                            output.append(0)
                        if (o != '' and o != 'Szczegóły'):
                            output.append(o)
                        if (l != None and gg != False):
                            output.append(l)
                            gg = False
                        o = ""
                    glob_output.append(output)
                    output = []
                next = serch_E.find('ul', class_="pagination").find_all('li', class_=None)
                amm = len(next)
                next = next[amm - 1]
                next = next.find('a', class_=None)

                if (next is not None):

                    next = next.get('href')
                    for jj in next:
                        try:
                            gg = int(jj)
                            num += jj
                        except:
                            None

                    if int(num) > int(self.last):
                        self.last = num
                        send(next)
                    else:
                        None

            send()
            return glob_output

    def Ranking(self):
        '''
        :return: zwraca tablice osob w rankingu w kolejnosci od most points to less points
        :exception: indexy poszczegolnych urzytkownikow
        0 - widoczna nazwa
        1 - nazwa urzytkownika
        3 - punkty
        '''
        rq = self.session

        cookies = rq.get(f"{self.ranked}")


        if 'csrftoken' in cookies.cookies:
            csrftoken = cookies.cookies['csrftoken']
        else:
            csrftoken = cookies.cookies['csrf']

        payload = {
            "csrfmiddlewaretoken": f"{csrftoken}",
            "login_view-current_step": "auth",
            "auth-username": self.login,
            "auth-password": self.password

        }

        data = rq.post(url=f"{self.ranked}", data=payload)
        zupa = bs(data.content, features='html.parser')

        tabela = []
        glob_table = []
        tab = zupa.find('table', class_="table table-ranking table-striped table-sm submission").find('tbody').find_all(
            'tr')
        for i in tab:
            pipn = i.find_all('td', class_="text-right sum-cell")
            user = i.find('td', class_="user-cell").text
            eee = i.find_all('td')
            for i in eee:
                pp = i.find('span')
                if (pp != None):
                    names = pp['data-username']

            ez = ""
            for ie in user:
                if (ie != '\n' or ie != " "):
                    ez += ie

            tabela.append(ez)
            tabela.append(names)
            iss = pipn[len(pipn) - 1]

            ezs = ""
            for j in iss.text:
                if (iss != '\n' or iss != " "):
                    ezs += j
            tabela.append(int(ezs))
            glob_table.append(tabela)
            tabela = []

        return glob_table

    def CheckErrors(self, link_to_zad=None):
        '''
        :param link_to_zad: Link do zadania do sprawdzenia
        :return: zwraca błedy jezeli są w dzienniku tablica bledow jest w tablicy o nazwie errors.
        Przykładowy dziennik : {"errors":[...,...,...,...]} gdzie kropki to błędy
        '''

        if link_to_zad is not None:
            bit = link_to_zad.replace("https://szkopul.edu.pl", "")
            link_prepared = f"{self.temp_url}{self.redirecotr}account/login/?next={bit}"

            rq = self.session

            cookies = rq.get(link_prepared)

            if 'csrftoken' in cookies.cookies:
                csrftoken = cookies.cookies['csrftoken']
            else:
                csrftoken = cookies.cookies['csrf']

            payload = {
                "csrfmiddlewaretoken": f"{csrftoken}",
                "login_view-current_step": "auth",
                "auth-username": self.login,
                "auth-password": self.password

            }

            data = rq.post(url=link_prepared, data=payload)
            zupa = bs(data.content, features='html.parser')

            dictionary = {

            }

            err = []
            try:
                obj = zupa.find('div', class_="row").find('div', class_="row").find_all('ul', class_="list-unstyled")
                for i in obj:
                    gg = i.find_all("li")
                    for jj in gg:
                        pp = jj.find_all("span")[1]
                        err.append(pp.text)

                dictionary['errors'] = err
                return dictionary
            except:
                return None