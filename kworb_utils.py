import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def extrair_top_artistas_spotify_kworb():
    url = "https://kworb.net/spotify/artists.html"  # Certifique-se de que esta é a URL correta

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontra a tabela com a classe 'addpos sortable'
        table = soup.find('table', {'class': 'addpos sortable'})

        if table:
            headers = [th.text.strip() for th in table.find_all('th')]
            data = []
            tbody = table.find('tbody') if table.find('tbody') else table
            rows = tbody.find_all('tr')

            for row in rows:
                cols = row.find_all('td')
                if cols:
                    # Extrai o nome do artista do link
                    artist_link = cols[0].find('a')  # Encontra a tag <a> dentro da primeira <td>
                    artist_name = artist_link.text.strip() if artist_link else "N/A"

                    # Extrai os outros dados
                    streams = cols[1].text.strip()
                    daily = cols[2].text.strip()
                    as_lead = cols[3].text.strip()
                    solo = cols[4].text.strip()
                    as_feature = cols[5].text.strip()

                    data.append([artist_name, streams, daily, as_lead, solo, as_feature])

            df = pd.DataFrame(data, columns=["Artist", "Streams", "Daily", "As lead", "Solo", "As feature"])
            return df
        else:
            print("Tabela de artistas com a classe 'addpos sortable' não encontrada.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    except Exception as e:
        print(f"Erro ao processar o HTML: {e}")
        return None