import copy 
class Rating:
	def __init__(self, rating_information):
		# {'rating': general_rating, 'percentages': rating_percentages, 'demographic': rating_by_demographic, 'us': us_rating, 'non-us':non_us_rating}

		self.general_rating = rating_information['rating']
		self.US_users = rating_information['us']
		self.non_US_users = rating_information['non-us']

		#'all_ages', '<18', '18-29', '30-44', '45+'
		self.all_age_based_rating = copy.deepcopy(rating_information['demographic'][0])
		self.male_rating = copy.deepcopy(rating_information['demographic'][1])
		self.female_rating = copy.deepcopy(rating_information['demographic'][2])

		self.rating_percentages =  copy.deepcopy(rating_information['percentages'])

	def __str__(self):
		return self.general_rating+'#'+self.US_users+'#'+self.non_US_users+'#'+str(self.rating_percentages)+'#'+str(self.all_age_based_rating)+'#'+str(self.female_rating)+'#'+str(self.male_rating)+'\n'