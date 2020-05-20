from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from textblob import TextBlob
from better_profanity import profanity
import os
from time import sleep

PATH = 'C:\Program Files (x86)\chromedriver.exe'  #provide path to chromedriver.exe here.

class ProfanityBot:
	def __init__(self, channel_url, vid_cnt, del_transcript= True):
		self.driver = webdriver.Chrome(PATH)
		self.channel_url = channel_url
		self.channel_name = ''
		self.vid_cnt = vid_cnt  #the number of videos to be fetched from channel.
		self.del_transcript = del_transcript

	def fetch_transcripts(self):
		self.driver.get(self.channel_url+"/videos")  #to jump on videos section.
		self.channel_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='inner-header-container']//div[@id='text-container']"))).text
		links = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.ID, "video-title")))
		print("Started process..")
		print("Scraping transcripts from {} channel...".format(self.channel_name))
		toggle = True
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
					sleep(2)
					# to toggle timestamp we just need to run this once.
					if toggle:
						WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ytd-menu-renderer[@class='style-scope ytd-engagement-panel-title-header-renderer']//button[@id='button']"))).click()
						WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ytd-menu-service-item-renderer[@class='style-scope ytd-menu-popup-renderer']"))).click()
						toggle = False  #once toggled, no need to toggle again.

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
			print('---------------------------------------------------------------------------------')
			#sending scraped transcript for sentiment and profanity analysis.
			self.profanity_analysis(filepath)  
			self.sentiment_analysis(filepath)
			# deleting transcripts after use.
			if self.del_transcript == True:
				os.remove(filepath)

	# Profanity analysis
	def profanity_analysis(self, filepath):
		curse_word_count = 0
		total_word_count = 0
		curse_words = []
		with open(filepath, 'r') as file:
			text = file.read()
			sentences = text.split('\n')
			for sentence in sentences:
				word_list = sentence.split(' ')
				for word in word_list:
					if profanity.contains_profanity(word):  #returns True if word is curse/swear/profane word.
						curse_words.append(word)
						curse_word_count += 1
					total_word_count += 1 
		profanity_percentage = (curse_word_count/total_word_count) * 100
		print(f'Curse words used: {curse_words}')
		print(f'Profanity/curse/swear percentage: {round(profanity_percentage, 5)}%') 

	# Sentiment analysis
	def sentiment_analysis(self, filepath):
		pos_count = 0
		neg_count = 0
		total_count = 0
		with open(filepath, 'r') as file:
			text = file.read()
			subjectivity = TextBlob(text).subjectivity
			sentence_li = text.split('\n')
			for sentence in sentence_li:
				blob = TextBlob(sentence)
				if blob.sentiment.polarity >= 0.1:
					pos_count += 1
				elif blob.sentiment.polarity < 0:
					neg_count += 1
				total_count += 1
		pos_sentiment = (pos_count/total_count) * 100
		neg_sentiment = (neg_count/total_count) * 100
		print(f'Positive sentiment: {round(pos_sentiment, 4)}%\nNegative sentiment: {round(neg_sentiment, 4)}%\nSubjectivity: {round(subjectivity, 4)}')

obj = ProfanityBot('https://www.youtube.com/channel/UC3DkFux8Iv-aYnTRWzwaiBA', 7)
obj.fetch_transcripts()

