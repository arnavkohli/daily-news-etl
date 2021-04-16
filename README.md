# Daily News ETL

A very basic pythonic script to aggregate from different news sources and cluster the headlines according to semantic similarities.

## Clustering Algorithm (WIP)

### For every headline received:
- Find the average similarity between the headline and sentences of each cluster
- Find the maximum average similarity 
- If the similarity is below a certain threshold, create a new cluster
- Else, append the headline to the cluster

