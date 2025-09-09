document.addEventListener('DOMContentLoaded', function() {
  const currentPath = window.location.pathname.split('/').pop();
  const navLinks = document.querySelectorAll('#navmenu ul li a');

  navLinks.forEach(link => {
    const linkPath = link.getAttribute('href');
    if (linkPath === currentPath) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Handle dropdown active state
  const dropdownLinks = document.querySelectorAll('#navmenu .dropdown > a');
  dropdownLinks.forEach(dropdownLink => {
    const dropdownItems = dropdownLink.nextElementSibling.querySelectorAll('a');
    dropdownItems.forEach(item => {
      if (item.getAttribute('href') === currentPath) {
        dropdownLink.classList.add('active');
        // Optionally, add active to the dropdown item itself if needed for styling
        item.classList.add('active');
      }
    });
  });
});
