document.addEventListener("DOMContentLoaded", function () {
    document.querySelector('.event-row').addEventListener('click', function (e) {
        if (e.target && e.target.matches("a.btn-primary[data-event-id]")) {
            e.preventDefault();
            const eventId = e.target.getAttribute('data-event-id');
            console.log(eventId);
            if (eventId) {
                fetch(`/event/${eventId}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Basic event details with safe fallbacks
                        document.getElementById('eventName').innerText = data.name ?? 'Not available';

                        // Safe data access using optional chaining and nullish coalescing
                        const venue = data._embedded?.venues?.[0];
                        document.getElementById('eventLocation').innerText = venue ? `${venue.name ?? 'Not available'}, ${venue.address?.line1 ?? 'Not available'}` : 'Not available';
                        document.getElementById('eventDate').innerText = data.dates?.start?.localDate ?? 'Not available';
                        document.getElementById('seatMapUrl').setAttribute('href', data.seatmap?.staticUrl ?? '#');
                        document.getElementById('venueAddress').innerText = venue?.address?.line1 ?? 'Not available';
                        document.getElementById('cityCountry').innerText = venue ? `${venue.city?.name ?? 'Not available'}, ${venue.country?.countryCode ?? 'Not available'}` : 'Not available';
                        
                        // Price range formatting with safe access
                        const priceRanges = data.priceRanges?.map(range => `$${range.min} - $${range.max}`).join(', ');
                        document.getElementById('priceRange').innerText = priceRanges ?? 'Not available';
                        document.getElementById('saleDates').innerText = data.sales?.public ? `Start: ${data.sales.public.startDateTime ?? 'Not available'}, End: ${data.sales.public.endDateTime ?? 'Not available'}` : 'Not available';
                        document.getElementById('firstImageUrl').setAttribute('src', data.images?.[0]?.url ?? '#');
                        document.getElementById('eventUrl').setAttribute('href', data.url ?? '#');
                        
                        // Attraction names and URLs with safe access and formatting
                        const attractions = data._embedded?.attractions?.map(attraction => `${attraction.name}: ${attraction.url}`).join('\n') ?? 'Not available';
                        document.getElementById('attractions').innerText = attractions;

                        // Handling boolean values and providing appropriate text
                        const ageRestrictionsText = data.ageRestrictions?.legalAgeEnforced ? 'Age restrictions apply' : 'No age restrictions';
                        document.getElementById('ageRestrictions').innerText = ageRestrictionsText;
                        document.getElementById('pleaseNote').innerText = data.pleaseNote ?? 'Not available';
                        document.getElementById('startEndDate').innerText = data.dates?.start?.localDate ? `Start: ${data.dates.start.localDate}, End: ${data.dates.start.localDate}` : 'Not available';
                        document.getElementById('ticketLimit').innerText = data.ticketLimit?.info ?? 'Not available';
                        document.getElementById('boxOfficeInfo').innerText = venue?.boxOfficeInfo?.openHoursDetail ?? 'Not available';
                        document.getElementById('generalInfo').innerText = venue?.generalInfo?.generalRule ?? 'Not available';

                        // Show the modal only after all data has been processed
                        var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
                        eventModal.show();
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        // Handle the error, e.g., show an error message to the user
                    });
            }
        }
    });
});
