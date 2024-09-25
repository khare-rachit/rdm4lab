document.addEventListener('DOMContentLoaded', function () {

    // Get all the navigation links within the sidebar
    const navLinks = document.querySelectorAll('#mainSidebar .nav-link');

    // Add event listener to each link
    navLinks.forEach(link => {
        link.addEventListener('click', function (event) {

            // Prevent default link behavior
            event.preventDefault();

            // Remove active class from all links
            navLinks.forEach(link => link.classList.remove('active'));

            // Add active class to the clicked link
            this.classList.add('active');

            // Save the active link in local storage
            window.location.href = this.href;
        });
    });

    // Function to remove active class from all links and set on the current link
    function setActiveLink(currentLink) {

        // Remove active class from all links
        navLinks.forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to the clicked link
        currentLink.classList.add('active');

        // Save the active link in local storage
        localStorage.setItem('activeNav', currentLink.href);
    }

    // Attach click event listeners to all nav links
    navLinks.forEach(link => {
        // Call setActiveLink function when a nav link is clicked
        link.addEventListener('click', function (event) {
            setActiveLink(this); // Set clicked link as active
        });
    });

    // Check local storage on page load to set the active class
    const activeNav = localStorage.getItem('activeNav');

    // If activeNav is found in local storage, set the active class
    if (activeNav) {
        const activeLink = Array.from(navLinks).find(link => link.href === activeNav);

        // If activeLink is found, add the active class
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }
});
