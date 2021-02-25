import pandas as pd
import re


def modify_country_data(df):
    # Juhul, kui filmi/sarja tegid mitu riiki, jätame alles vaid ühe
    df['country'] = df['country'].apply(keep_first)

    # Jätame alles unikaalsed riigid, sorteerime need, eemaldame tühja väärtuse, loome sõnastiku, kus võtmeteks on
    # riikide nimed ja väärtusteks on ID-d (alates 1st kasvavalt), asendame riikide nimed ID-dega
    unique_countries = sorted(df['country'].unique().tolist())
    unique_countries.remove("")
    countries_dict = {unique_countries[i]: i + 1 for i in range(0, len(unique_countries))}
    df = df.replace({"country": countries_dict})

    # Loome ümberpööratud võtme-väärtuse paaridega sõnastiku, loome riikidele vastava DataFrame'i, määrame
    # indeksiveeru nimeks 'id'
    reverse_countries_dict = dict([(value, key) for key, value in countries_dict.items()])
    countries_df = pd.DataFrame.from_dict(reverse_countries_dict, orient='index', columns=['nimi'])
    countries_df.index.name = 'id'

    # Lisame riikide DataFrame'le uued veerud ja täidame need tühjade sõnedega
    countries_df['rahvastikuarv'] = [""] * len(countries_df['nimi'].tolist())
    countries_df['pindala'] = [""] * len(countries_df['nimi'].tolist())
    countries_df['skp'] = [""] * len(countries_df['nimi'].tolist())
    countries_df['interneti_kasutajad'] = [""] * len(countries_df['nimi'].tolist())

    # Loeme sisse .csv faili, kus on andmeid (rahvastikuarv, pindala, skp elaniku kohta, interneti kasutajaid 100
    # inimese kohta jne), mille lisame igale riigile
    additional_country_data_df = pd.read_csv('../Algandmed/country_profile_variables.csv', encoding='utf8',
                                             index_col=False)

    # Loome listid hetkel tühjade veergude jaoks, mille abil saame vastavad väärtused hiljem DataFrame'i lisada
    populations = []
    areas = []
    gdps = []
    internet_users = []
    # Käime läbi kõik riigid riikide DataFrame's (riigid on siinkohal tähestiku järjekorras), leiame riigi nime abil
    # hiljuti sisse loetud lisaandmete failist lisaandmeid vastava riigi kohta ja lisame need eelnevalt loodud
    # vastavasse listi (population, areas, gdps või internet_users)
    for country in countries_df['nimi']:
        try:
            temp_df = additional_country_data_df.loc[additional_country_data_df.country == country]
            if not temp_df.empty:
                # Korrutame rahvaaarvu tuhandega, kuna lisaandmetes oli rahvaarv tuhandetes
                population = temp_df['Population in thousands (2017)'].values[0]
                if population == -99:
                    populations.append("")
                else:
                    populations.append(int(population * 1000))

                area = temp_df['Surface area (km2)'].values[0]
                if area == -99:
                    areas.append("")
                else:
                    areas.append(area)

                # Korrutame SKP väärtuse 0.82-ga, sest Google'st otsides oli 25/02/2021 seisuga 1 dollar väärt 0.82
                # eurot
                gdp = temp_df['GDP per capita (current US$)'].values[0]
                if gdp == -99:
                    gdps.append("")
                else:
                    gdps.append(round((gdp * 0.82), 1))

                # Asendame interneti kasutajate väärtuses olnud ',' '.'-ga ning lõpuks ümardame selle täisarvuks
                internet_user = temp_df['Individuals using the Internet (per 100 inhabitants)'].values[0]
                if internet_user == -99:
                    internet_users.append("")
                else:
                    internet_users.append(int(round(float(str(internet_user).replace(",", ".")))))
            # Kui mingi riigi kohta lisaandmeid ei leidnud, lisame igasse listi tühja väärtuse (sõne)
            else:
                populations.append("")
                areas.append("")
                gdps.append("")
                internet_users.append("")
        # Kui esineb mingi probleem lisaandmete saamisel, lisame igasse listi tühja väärtuse (sõne)
        except KeyError:
            populations.append("")
            areas.append("")
            gdps.append("")
            internet_users.append("")

    # Asendame riikide DataFrame'i veergude väärtused listidest saadud väärtustega
    countries_df['rahvastikuarv'] = populations
    countries_df['pindala'] = areas
    countries_df['skp'] = gdps
    countries_df['interneti_kasutajad'] = internet_users

    # Kirjutame DataFrame'i riigid.csv faili
    countries_df.to_csv('riigid.csv', encoding='utf8', header=False)

    # Tagastame üldise DataFrame'i, milles asendasime riikide nimed ID-dega
    return df


def modify_people_data(df):
    # Loome listi kõigi näitlejate ja lavastajate nimede jaoks
    all_people = []
    # Käime läbi kõik näitlejad ja lavastajad üldises DataFrame's ning lisame nad listi all_people, kui neid seal juba
    # ei ole
    for people_type in ['cast', 'director']:
        for person in df[people_type]:
            if str(person) != "nan":
                if "," in person:
                    people = person.split(",")
                    for p in people:
                        if p.strip() not in all_people:
                            all_people.append(p.strip())
                else:
                    if person.strip() not in all_people:
                        all_people.append(person.strip())

    # Igaks juhuks teisendame listi hulgaks ja tagasi listiks ning sorteerime selle, et ükski nimi ei korduks ja et
    # nimed oleks tähestiku järjekorras
    unique_people = sorted(list(set(all_people)))

    # Loome kaks sõnastikku, millest ühes on võtmeteks inimeste nimed ja väärtusteks ID-d (alates 1st kasvavalt) ning
    # teises on võtmed ja väärtused vastupidiselt
    people_dict = {unique_people[i]: i + 1 for i in range(0, len(unique_people))}
    reverse_people_dict = dict([(value, key) for key, value in people_dict.items()])
    # Loome tagurpidise sõnastiku põhjal kõigi isikute DataFrame'i ja kirjutame selle isikud.csv faili
    people_df = pd.DataFrame.from_dict(reverse_people_dict, orient='index', columns=['nimi'])
    people_df.index.name = 'id'
    people_df.to_csv('isikud.csv', encoding='utf8', header=False)

    # Käime läbi kõik näitlejad üldises DataFrame's, kui näitlejaid on mitu, loome iga näitleja ja vastava filmi põhjal
    # kolmeelemendilise listi kujuga [id, teose_id, näitleja_id] ja lisame selle omakorda listi acting_csv_rows, kui
    # näitlejaid on üks teeme vaid ühe kolmeelemendilise listi ja lisame selle samuti list acting_csv_rows
    df_row_index = 1
    acting_csv_id = 1
    acting_csv_rows = []
    for actors in df['cast']:
        if str(actors) != "nan":
            if "," in actors:
                row_actors = actors.split(",")
                for row_actor in row_actors:
                    actor_id = people_dict[row_actor.strip()]
                    movie_id = df_row_index
                    acting_csv_rows.append([acting_csv_id, movie_id, actor_id])
                    acting_csv_id += 1
            else:
                actor_id = people_dict[actors.strip()]
                movie_id = df_row_index
                acting_csv_rows.append([acting_csv_id, movie_id, actor_id])
                acting_csv_id += 1
        df_row_index += 1

    # Teeme acting_csv_rows põhjal näitlemise DataFrame'i ning kirjutame selle faili näitlemine.csv
    acting_df = pd.DataFrame(acting_csv_rows, columns=['id', 'teose_id', 'naitleja_id'])
    acting_df.to_csv('näitlemine.csv', encoding='utf8', index=False, header=False)

    # Käime läbi kõik lavastajad üldises DataFrame's, kui lavastajaid on mitu, loome iga lavastaja ja vastava filmi
    # põhjal kolmeelemendilise listi kujuga [id, teose_id, lavastaja_id] ja lisame selle omakorda listi
    # directing_csv_rows, kui lavastajaid on üks teeme vaid ühe kolmeelemendilise listi ja lisame selle samuti list
    # directing_csv_rows
    df_row_index = 1
    directing_csv_id = 1
    directing_csv_rows = []
    for directors in df['director']:
        if str(directors) != "nan":
            if "," in directors:
                row_directors = directors.split(",")
                for row_director in row_directors:
                    director_id = people_dict[row_director.strip()]
                    movie_id = df_row_index
                    directing_csv_rows.append([directing_csv_id, movie_id, director_id])
                    directing_csv_id += 1
            else:
                director_id = people_dict[directors.strip()]
                movie_id = df_row_index
                directing_csv_rows.append([directing_csv_id, movie_id, director_id])
                directing_csv_id += 1
        df_row_index += 1

    # Teeme directing_csv_rows põhjal näitlemise DataFrame'i ning kirjutame selle faili näitlemine.csv
    directing_df = pd.DataFrame(directing_csv_rows, columns=['id', 'teose_id', 'lavastaja_id'])
    directing_df.to_csv('lavastamine.csv', encoding='utf8', index=False, header=False)

    # Kustutame üldisest DataFrame'st lavastajate ja näitlejate veerud, sest neid pole seal enam vaja
    del df['director']
    del df['cast']

    # Tagastame üldise DataFrame'i, millest eemaldasime kaks veergu
    return df


def modify_show_movie_data(df):
    # Kui tegemist on filmiga, asendame veeru type väärtuse 1-ga, vastasel juhul (kui tegemist on sarjaga) asendame
    # veeru väärtuse 0-ga
    df['type'] = df['type'].apply(lambda x: 1 if x == 'Movie' else 0)
    # Kui teos on liigitatud mitme žanri alla, jätame alles vaid esimese
    df['listed_in'] = df['listed_in'].apply(keep_first)
    # Teisendame teose lisamise kuupäeva SQL-le sobivale kujule
    df['date_added'] = df['date_added'].apply(format_date)
    df.columns = ['on_film', 'pealkiri', 'riigi_id', 'lisamise_kuupaev', 'valjalaske_aasta', 'vanusepiirang', 'kestus',
                  'zanr', 'kirjeldus']
    df.index.names = ['id']

    # Tagastame üldise DataFrame'i, milles muutsime mitut veergu
    return df


def format_date(date):
    # Teisendame kuupäevad SQL-le sobivale kujule, näiteks 'January 15, 2020' asemel '2020-01-15'
    date = str(date).strip()
    if date != "" and date != "nan":
        month_dict = {
            "January": "01",
            "February": "02",
            "March": "03",
            "April": "04",
            "May": "05",
            "June": "06",
            "July": "07",
            "August": "08",
            "September": "09",
            "October": "10",
            "November": "11",
            "December": "12",
        }
        split_date = re.split(",\\s|\\s", date)
        split_date = [x.strip() for x in split_date]
        month = month_dict[split_date[0]]
        day = split_date[1] if len(split_date[1]) == 2 else "0" + split_date[1]
        year = split_date[2]
        date = year + "-" + month + "-" + day
    else:
        date = ""
    return date


def keep_first(x):
    # Kui sõnes on mitu alamsõne (eraldatud komadega) tagastame neist vaid esimese
    if str(x) == "nan":
        return ""
    else:
        if "," in x:
            return x.split(",")[0].strip()
        else:
            return x.strip()


def create_csvs():
    # Loeme üldisesse DataFrame'i sisse algsed Netflixi andmed
    df = pd.read_csv('../Algandmed/netflix_titles.csv', encoding='utf8', index_col=False)

    # Eemaldame veeru 'show_id' väärtuste eest esimese sümboli (täht 's') ja määrame veeru 'show_id' indeks-veeruks
    df['show_id'] = df['show_id'].apply(lambda x: x[1:])
    df = df.set_index('show_id')

    # Muudame/loome riikidega seotud andmeid
    df = modify_country_data(df)

    # Muudame/loome isikutega seotud andmeid
    df = modify_people_data(df)

    # Muudame/loome teostega seotud andmeid
    df = modify_show_movie_data(df)

    # Kirjutame üldise DataFrame'i faili teosed.csv, sest üldisesse DataFrame'i on alles jäänud vaid teostega seotud
    # andmed
    df.to_csv('teosed.csv', encoding='utf8', header=False)


create_csvs()
