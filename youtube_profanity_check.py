from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os

PATH = 'C:\Program Files (x86)\chromedriver.exe'  #provide path to chromedriver.exe here.

class ProfanityBot:
	def __init__(self, channel_url, vid_cnt):
		self.driver = webdriver.Chrome(PATH)
		self.channel_url = channel_url
		self.channel_name = ''
		self.vid_cnt = vid_cnt  #the number of videos to be fetched from each channel.

	def fetch_transcripts(self):
		self.driver.get(self.channel_url+"/videos")  #to jump on videos section.
		self.channel_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='inner-header-container']//div[@id='text-container']"))).text
		links = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.ID, "video-title")))
		print("Started process..")
		print("Scraping transcripts from {} channel...".format(self.channel_name))
		try:
			count = 0
			links_list = []
			# got all links for given channel
			for item in links[0:self.vid_cnt]:
				links_list.append(item.get_attribute('href'))

			#looping through each link and fetching transcripts. 
			for link in links_list:
				self.driver.get(link)
				opt_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body/ytd-app/div[@id='content']/ytd-page-manager[@id='page-manager']/ytd-watch-flexy[@class='style-scope ytd-page-manager hide-skeleton']/div[@id='columns']/div[@id='primary']/div[@id='primary-inner']/div[@id='info']/div[@id='info-contents']/ytd-video-primary-info-renderer[@class='style-scope ytd-watch-flexy']/div[@id='container']/div[@id='info']/div[@id='menu-container']/div[@id='menu']/ytd-menu-renderer[@class='style-scope ytd-video-primary-info-renderer']/yt-icon-button[@id='button']/button[1]")))
				opt_btn.click()
				# if transcript btn doesn't exit for a video or if transcipts section doesn't show up.
				try:
					transcript_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-popup-container.style-scope.ytd-app:nth-child(13) iron-dropdown.style-scope.ytd-popup-container:nth-child(1) div.style-scope.iron-dropdown ytd-menu-popup-renderer.style-scope.ytd-popup-container paper-listbox.style-scope.ytd-menu-popup-renderer:nth-child(1) > ytd-menu-service-item-renderer.style-scope.ytd-menu-popup-renderer:nth-child(2)")))
					transcript_btn.click()
					# # to toggle timestamp(just reomve 2 lines from below if you you wanna keep timestamp)
					# WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ytd-menu-renderer[@class='style-scope ytd-engagement-panel-title-header-renderer']//button[@id='button']"))).click()
					# WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ytd-menu-service-item-renderer[@class='style-scope ytd-menu-popup-renderer']"))).click()
					transcript_text = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-transcript-body-renderer"))).text
					count += 1
				except:
					count += 1
					print(f"no transcipt found for {count}th video!")
					continue #will go for next iteration of current for loop.
			
				# to append transcript text to a file
				filename = f'{self.channel_name}.txt'
				filepath = os.path.join("scraped_transcripts", filename)
				with open(filepath, 'a') as file:
					file.write(transcript_text)
				print(f'{count}th video done.')

		except Exception as e:
			print(e)
		
		finally:
			self.driver.quit()
			print(f'Done scraping transcripts of {self.vid_cnt} videos from {self.channel_name} channel.')


blob = ProfanityBot('https://www.youtube.com/channel/UC4JX40jDee_tINbkjycV4Sg', 7)
blob.fetch_transcripts()




# from textblob import TextBlob
# curse_words = ["fuck", "fuck you", "fuck off", "shit", "piss off", "dick head", "asshole", "son of a bitch", "bastard", "bitch", "damn", "cunt", "bloody hell", "bollocks", "bugger", "rubbish", "shag", "twat", "bloody oath", "fuck me"]
# line = "That car is mine! I loved that car. You better keep your fuck out of that car. Fuck off you jerk! I hate you bitch"
# blob = TextBlob(line)
# print(blob.sentiment)
# print(blob.words.count("i"))

