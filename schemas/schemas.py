LOGIN_SCHEMA = { \
	"type" : "object", \
	"required" : ["username", "password"], \
	"properties" : { \
		"username" : {"type" : "string"}, \
		"password" : {"type" : "string"}, \
	}, \
}

ADD_USER_LINK_SCHEMA = { \
	"type" : "object", \
	"required" : ["content"], \
	"properties" : { \
		"content" : {"type" : "string"}, \
	}, \
}

REMOVE_USER_LINK_SCHEMA = { \
	"type" : "object", \
	"required" : ["link"], \
	"properties" : { \
		"link" : {"type" : "string"}, \
	}, \
}

GET_LINK_SCHEMA = { \
	"type" : "object", \
	"required" : ["link"], \
	"properties" : { \
		"link" : {"type" : "string"}, \
	}, \
}

ADD_CONTENT_SCHEMA = { \
	"type" : "object", \
	"required" : ["content"], \
	"properties" : { \
		"content" : {"type" : "string"}, \
	}, \
}
