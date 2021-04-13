import requests
import re, json, datetime
from scipy import spatial
from sent2vec.vectorizer import Vectorizer

CLUSTERS = {
}
vectorizer = Vectorizer()

def get_average_cos_dist(sentence, ls):
	vectorizer.bert([sentence] + ls)
	vectors_bert = vectorizer.vectors

	avg = 0
	count = 0
	for index, vector in enumerate(vectors_bert):
		if index == 0:
			continue
		cos_dist = spatial.distance.cosine(vectors_bert[0], vectors_bert[index])
		avg = (avg * count + cos_dist) / (count + 1)
		return avg
		count += 1
	return avg


def add_to_cluster(ls):
	'''
		Assumption:
			Each data source has unique titles (all their titles are of different categories)
	'''
	if CLUSTERS == {}:
		for index, title in enumerate(ls):
			CLUSTERS[index] = {
				"sentences" : [title]
			}
	else:
		for index, title in enumerate(ls):
			minAvgCosDist, minIndex = 10 ** 9, None

			for categInd in CLUSTERS:
				sentences = CLUSTERS[categInd].get("sentences")
				avgCosDist = get_average_cos_dist(title, sentences)

				if avgCosDist < minAvgCosDist:
					minAvgCosDist, minIndex = avgCosDist, categInd
			if minAvgCosDist > 0.12:
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
			"referer": self.base_url,
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
	add_to_cluster(list1[:10])
	print (f"Len List1: {len(list1)}")
	print (CLUSTERS)

	nyt_url, nyt_ep, nyt_p = "https://www.nytimes.com", "/section/world", r'<a[^>]*>([^<]+)</a></h2>'
	nyt_ds = DataSource(nyt_url)
	list2 = nyt_ds.find_all_matches(nyt_ep, nyt_p)
	add_to_cluster(list2[:10])
	print (f"Len List2: {len(list2)}")
	print (CLUSTERS)

	with open("clusters.json", "w") as f:
		json.dump(CLUSTERS, f, indent=4)

	timeEnd = datetime.datetime.now()

	print (f"Time Taken: {timeEnd - timeStart}")

	with open("data.json", "w") as f:
		json.dump({"list1" : list1, "list2": list2}, f, indent=4)

	
