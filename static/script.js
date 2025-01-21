    // JavaScript function to show an image on hover
    function highlight(area, hoverImageSrc) {
        // Get the hover image element
        const hoverImage = document.getElementById('hover-image');
        
        // Change the source of the hover image based on the area hovered
        hoverImage.src = hoverImageSrc;

        // Make the hover image visible
        hoverImage.style.display = 'block';

        // Position the hover image relative to the main image
        const rect = area.getBoundingClientRect();
        const mainImage = document.querySelector('.main-image').getBoundingClientRect();

        // Adjust hover image position so it's over the main image
        hoverImage.style.top = `${rect.top - mainImage.top + window.scrollY}px`; // Adjust position if needed
        hoverImage.style.left = `${rect.left - mainImage.left + window.scrollX}px`; // Adjust position if needed
    }

    // JavaScript function to hide the hover image when mouse leaves the area
    function removeHighlight() {
        const hoverImage = document.getElementById('hover-image');
        hoverImage.style.display = 'none';
    }