// Ensuring document is loaded

    document.addEventListener('DOMContentLoaded', () => {


        // Navbar checker

        // Changing active status in the navbar
        const links = document.querySelectorAll(".nav-link");
        const page = window.location.pathname;

        links.forEach(link => {
            if (link.pathname === page) {
                link.classList.add("active");
            }
            else if (link.pathname === '/register/') {
                if (page === '/register/teacher' || page === '/register/student') {
                    link.classList.add("active");
                }
            }
            else {
                link.classList.remove("active");
            }
        });


        // Like Increaser

        // Function that increases like count
        function like(id, type, element) {

            // Fetch call to API
            fetch(`/like/${id}/${type}`)
            .then(response => response.json())
            .then(status => {
                // Checking for sucess message
                if ('success' in status) {

                    // Updating likecount taking number from server
                    let likeCount = status.likecount
                    element.innerHTML = likeCount

                }
            })
        }

        // Gathering all types of threads and comments
        const thread = document.querySelectorAll('#thread-like')

        // Looping through threads
        thread.forEach(element => {

            // Getting post information
            let postId = element.dataset.id
            let postType = element.dataset.type
            let likeHTML = element.querySelector('#like-count')

            // Event listener for click to trigger like function
            element.onclick = () => {
                like(postId, postType, likeHTML)
            }

        })


        // Replying to threads

        // Getting all the reply buttons
        const replyButton = document.querySelectorAll('#thread-reply-button')

        // Looping through each button
        replyButton.forEach(element => {

            // Adding event listener
            element.onclick = () => {

                // Getting parent div
                let parent = element.parentElement

                // Changing display to inline of comment thread
                parent.querySelector('#thread-reply').style.display = 'inline'

            }

        })

    })