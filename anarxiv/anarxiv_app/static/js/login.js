function renderLoggedInView(){
	if (user) {
		document.getElementById("userNameField").innerHTML=user;
		location.reload();
	} else {
		location.reload();
	}
};

function loginAttempt(){


	var loginUser = document.getElementById("loginUser").value;
	var loginPassword = document.getElementById("loginPassword").value;

	$.ajax({
		type: "POST",
		url: "/home/login/",
		data: {"user" : loginUser, "password" : loginPassword}, 
		datatype: "JSON",

		success: function(data) {

			if (data["loginError"]) {
				$("#loginErrorMessage").removeClass("hidden");
			} 
			else {
				user = data["username"];
				renderLoggedInView();
				$("#loginModal").modal("hide");
				location.reload();
			}
		},

		error: function(jqXHR, textStatus, errorThrown) {
			$("#loginServerError").removeClass("hidden");
		}


	})

};

function logout(){
	$.ajax({
		type: "GET",
		url: "/home/logout/",

		success: function(data){
			if (data["success"]){
				user = null;
				renderLoggedInView();
			} else {
				$("#logoutErrorMessage").removeClass("hidden");
			}
		},

		error: function(jqXHR,textStatus,errorThrown){
			$("#logoutErrorMessage").removeClass("hidden");
		}
	})
}

