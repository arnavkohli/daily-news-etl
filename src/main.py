import requests
import re, json, datetime
from scipy import spatial
# from sent2vec.vectorizer import Vectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

CLUSTERS = {
}
# vectorizer = Vectorizer()

def get_average_cos_dist(sentence, ls):
	avg = 0
	count = 0
	X_list = word_tokenize(sentence) 

	for index, other in enumerate(ls):
		# tokenization
		Y_list = word_tokenize(other)
		  
		# sw contains the list of stopwords
		sw = stopwords.words('english') 
		l1 =[];l2 =[]
		  
		# remove stop words from the string
		X_set = {w for w in X_list if not w in sw} 
		Y_set = {w for w in Y_list if not w in sw}
		  
		# form a set containing keywords of both strings 
		rvector = X_set.union(Y_set) 
		for w in rvector:
		    if w in X_set: l1.append(1) # create a vector
		    else: l1.append(0)
		    if w in Y_set: l2.append(1)
		    else: l2.append(0)
		c = 0
		  
		# cosine formula 
		for i in range(len(rvector)):
		    c+= l1[i]*l2[i]
		cosine = c / float((sum(l1)*sum(l2))**0.5)
		avg = (avg * count + cosine) / (count + 1)

		count += 1
	return avg


def add_to_cluster(ls):
	'''
		Assumption:
			Each data source has unique titles (all their titles are of different categories)
	'''
	if CLUSTERS == {}:
		CLUSTERS[0] = {
			"sentences" : [ls[0]]
		}
		return add_to_cluster(ls[1:])
		# for index, title in enumerate(ls):
		# 	CLUSTERS[index] = {
		# 		"sentences" : [title]
		# 	}
	else:
		for index, title in enumerate(ls):
			minAvgCosDist, minIndex = 0, None

			for categInd in CLUSTERS:
				sentences = CLUSTERS[categInd].get("sentences")
				avgCosDist = get_average_cos_dist(title, sentences)

				if avgCosDist > minAvgCosDist:
					minAvgCosDist, minIndex = avgCosDist, categInd
			if minAvgCosDist < 0.05:
				CLUSTERS[len(CLUSTERS)] = {"sentences" : [title]}
			else:
				CLUSTERS[minIndex]["sentences"].append(title)


class DataSource:
	def __init__(self, base_url):
		self.base_url = base_url

	def get_page_text(self, endpoint):
		headers = {
			"accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"accept-encoding" : "gzip, deflate, br",
			"accept-language" : "en-US,en;q=0.9",
			# "referer": self.base_url,
			"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
		}
		page = requests.get(f"{self.base_url}{endpoint}", headers=headers)
		with open("output.html", "w") as f:
			f.write(page.text)
		return page.text

	def find_all_matches(self, endpoint, pattern):
		text = self.get_page_text(endpoint)
		if type(pattern) == type([]):
			res = []
			for p in pattern:	res += re.findall(p, text)
			return res
		else:
			return re.findall(pattern, text)


if __name__ == '__main__':
	timeStart = datetime.datetime.now()

	wsj_url, wsj_ep, wsj_p = "https://www.wsj.com", "/news/world", [r'<a[^>]*>([^<]+)</a></h2>', r'<a[^>]*>([^<]+)</a></h3>'] 
	wsj_ds = DataSource(wsj_url)
	list1 = wsj_ds.find_all_matches(wsj_ep, wsj_p)
	print (list1)
	add_to_cluster(list1)
	print (f"Len List1: {len(list1)}")
	print (CLUSTERS)

	nyt_url, nyt_ep, nyt_p = "https://www.nytimes.com", "/section/world", r'<a[^>]*>([^<]+)</a></h2>'
	nyt_ds = DataSource(nyt_url)
	list2 = nyt_ds.find_all_matches(nyt_ep, nyt_p)
	add_to_cluster(list2)
	print (f"Len List2: {len(list2)}")
	print (CLUSTERS)

	bbc_url, bbc_ep, bbc_p = "https://www.bbc.com", "/news/world", [r'<h2[^>]*>([^<]+)</h2></a>', r'<h3[^>]*>([^<]+)</h3></a>'] 
	bbc_ds = DataSource(bbc_url)
	list3 = bbc_ds.find_all_matches(bbc_ep, bbc_p)
	print (list3)
	add_to_cluster(list3)
	print (f"Len List2: {len(list3)}")
	print (CLUSTERS)

	atl_url, atl_ep, atl_p = "https://www.economist.com", "/", [r'<h2[^>]*>([^<]+)</h2></a>', r'<h3[^>]*>([^<]+)</h3></a>'] 
	atl_ds = DataSource(atl_url)
	list4 = atl_ds.find_all_matches(atl_ep, atl_p)
	print (list4)
	add_to_cluster(list4)
	print (f"Len List2: {len(list4)}")
	print (CLUSTERS)


	with open("clusters.json", "w") as f:
		json.dump(CLUSTERS, f, indent=4)

	timeEnd = datetime.datetime.now()

	print (f"Time Taken: {timeEnd - timeStart}")

	with open("data.json", "w") as f:
		json.dump({"list1" : list1, "list2": list2, "list3": list3, "list4" : list4}, f, indent=4)

	
