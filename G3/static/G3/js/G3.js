document.addEventListener('DOMContentLoaded', function () {

    // Get all the navigation tab links
    const allTabs = document.querySelectorAll('#analysisTabs .nav-link');
    const allPanes = document.querySelectorAll('#analysisTabContent .tab-pane');

    // Attach click event listeners to all tabs
    allTabs.forEach(link => {
        // Call setActiveLink function when a nav link is clicked
        link.addEventListener('click', function (event) {
            setActiveLink(this); // Set clicked link as active
        });
    });

    // Function to remove active class from all links and set on the current link
    function setActiveLink(currentLink) {

        // Remove active class from all links
        allTabs.forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to the clicked link
        currentLink.classList.add('active');

        // Get the corresponding pane element
        const paneId = currentLink.getAttribute('data-bs-target');
        const activePane = document.querySelector(paneId);

        // Remove active class from all panes
        allPanes.forEach(pane => {
            pane.classList.remove('active');
        });

        // Add active class to the corresponding pane
        activePane.classList.add('active');
        console.log('activePane:', activePane);
        // Save the active link in local storage
        localStorage.setItem('activeTab', currentLink.getAttribute('data-bs-target'));
    }

    // Check local storage on page load to set the active class
    const activeTab = localStorage.getItem('activeTab');
    console.log('activeTab:', activeTab); // 'activeTab: #tab1

    // If activeTab is found in local storage, set the active class
    if (activeTab) {
        const activeLink = Array.from(allTabs).find(link => link.getAttribute('data-bs-target') === activeTab);
        // If activeTab is found, add the active class
        if (activeLink) {
            setActiveLink(activeLink);
        }
    }
});
