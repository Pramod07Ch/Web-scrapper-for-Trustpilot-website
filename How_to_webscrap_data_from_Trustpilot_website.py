# import libraries
import requests
from bs4 import BeautifulSoup
from string import punctuation
import re
import pandas as pd
import time
import json

def get_containers_from_data(soup):
        '''
        get data in the form of containers from html parser
            - can add or delete required information from the reviews
        '''

        reviwers_container = soup.find_all('div', class_ ='consumer-information__name')

        body_container = soup.find_all('div', class_ = 'review-content__body')

        star_ratings_container = soup.find_all('div', class_ = 'star-rating star-rating--medium')

        ratings_container = soup.find_all('div', class_ = 'star-rating star-rating--medium')

        dates_container = soup.find_all('div', class_ ='review-content-header__dates')

        reviews_posted_container = soup.find_all('div', class_ = 'consumer-information__review-count')

        ## profile
        user_info = soup.find_all('aside', 'review__consumer-information')

        return reviwers_container, body_container, star_ratings_container, ratings_container, dates_container, reviews_posted_container, user_info

def create_dataframe_and_save(reviewer, title, content, star_rating, rating, date, reviews_posted, location):
    '''
    Create a dataframe and save as .csv file

    '''
    print('*** creating a dataframe *** \n')
    # create a dataframe
    reviews_df = pd.DataFrame(list(zip(reviewer, title, content, star_rating, rating, date, reviews_posted, location)),
                      columns = ['Reviewer','Title','Content', 'Star_rating', 'Rating', 'Date', 'Reviews_posted', 'Location'])

    print('*** created a dataframe *** \n')

    # formatting
    reviews_df.Star_rating = reviews_df.Star_rating.astype('int')
    reviews_df.Reviews_posted = reviews_df.Reviews_posted.astype('int')
    reviews_df.Date = pd.to_datetime(reviews_df.Date)
    print('** formated the dataframe ***\n')

    print('*** info of the dataframe ***')
    reviews_df.info()

    # save the file as .csv
    reviews_df.to_csv('web_scraped.csv', index=False)

    print('Saved as .csv file to local working disk')


def web_scraping(URL, num_pages, sleep_time=0.2):
    '''
    Web scrapng data from Trustpilot website
    Params:
        URL : str
        num_pages : int
     
    '''
    # URL = 'https://www.trustpilot.com/review/tesla.com?page='
    print(' Web scraping for reviews \n')
    reviewer =[]
    title = []
    content = []
    star_rating = []
    rating = []
    date = []
    reviews_posted = []
    location = []

    for page in range(1, num_pages):

        time.sleep(sleep_time)

        # request url
        html_text = requests.get(f'{URL}{page}')

        soup = BeautifulSoup(html_text.text, 'html.parser')

        # create containers of required data

        reviwers_container, body_container, star_ratings_container, ratings_container, \
            dates_container, reviews_posted_container, user_info = get_containers_from_data(soup)
        

        for x in range( len(reviwers_container)):

            # name
            reviewer_x = reviwers_container[x].text.strip()
            reviewer.append(reviewer_x)

            # title
            title_x = body_container[x].h2.text.strip()
            title.append(title_x)

            # content
            ## check wether review is written or empty
            if body_container[x].p is None:
                content.append('')
            else: 
                content_x = body_container[x].p.text.strip()
                content.append(content_x)

            # star rating
            star_rating_x = star_ratings_container[x].find('img')['alt'][0]
            star_rating.append(star_rating_x)

            # rating
            rating_x = ratings_container[x].find('img')['alt'][8:]
            rating.append(rating_x)

            # date
            ## updated
            date_x = json.loads(dates_container[x].find('script').contents[0])['publishedDate'][:10]
            # date_x = dates_container[x].script.text.strip()[18:28]
            date.append(date_x)

            # num reviews
            num_reviews_x = reviews_posted_container[x].text.strip('\nreviews')
            reviews_posted.append(num_reviews_x)

            # profile
            link = 'https://www.trustpilot.com'+ user_info[x].a['href']
            user_profile = requests.get(f'{link}')

            profile_soup = BeautifulSoup(user_profile.text, 'html.parser')
            location_x = profile_soup.find('div', class_ = 'user-summary-location').text.strip()
            location.append(location_x)

        if page%5==0:
            print('page number {}/ {} is done.'.format(page, num_pages))

    # create and save the data to local working disk
    create_dataframe_and_save(reviewer, title, content, star_rating, rating, date, reviews_posted, location)

   
if __name__ == "__main__":

    URL = input('Enter URL of brand page from trustpilot. eg. https://www.trustpilot.com/review/www.nikestore.com... :')
    num_pages = input('Enter number of pages :')
    
    # format the URL
    URL_page = URL + '?page='+num_pages
    
    web_scraping(URL_page, int(num_pages))
