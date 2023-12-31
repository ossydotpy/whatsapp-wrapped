// Select all image containers
const imageContainers = document.querySelectorAll('.image-container');

imageContainers.forEach(container => {
  const image = container.querySelector('img');
  const description = container.querySelector('.image-description');

  // Initially hide the description
  description.style.display = 'none';

  // Add event listener for touch or mouse click
  image.addEventListener('click', () => {
    description.style.display = description.style.display === 'none' ? 'block' : 'none'; // Toggle visibility
  });
});
