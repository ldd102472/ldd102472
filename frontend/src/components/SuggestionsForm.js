import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SuggestionsForm = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    rating: 5,
    is_anonymous: false,
    user_email: '',
    user_name: '',
    expected_benefit: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const categories = [
    { value: 'user_interface', label: 'User Interface' },
    { value: 'social_features', label: 'Social Features' },
    { value: 'content', label: 'Content' },
    { value: 'functionality', label: 'Functionality' },
    { value: 'performance', label: 'Performance' },
    { value: 'security', label: 'Security' },
    { value: 'accessibility', label: 'Accessibility' },
    { value: 'other', label: 'Other' }
  ];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const submitData = { ...formData };
      
      // If anonymous, remove user info
      if (formData.is_anonymous) {
        delete submitData.user_email;
        delete submitData.user_name;
      }

      const response = await axios.post(`${API}/suggestions`, submitData);
      
      if (response.status === 200) {
        setSubmitStatus({
          type: 'success',
          message: 'Thank you for your suggestion! We appreciate your innovative ideas.'
        });
        // Reset form
        setFormData({
          title: '',
          description: '',
          category: '',
          rating: 5,
          is_anonymous: false,
          user_email: '',
          user_name: '',
          expected_benefit: ''
        });
      }
    } catch (error) {
      console.error('Error submitting suggestion:', error);
      setSubmitStatus({
        type: 'error',
        message: 'Failed to submit suggestion. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const StarRating = ({ rating, onRatingChange }) => {
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onRatingChange(star)}
            className={`w-8 h-8 transition-colors ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            } hover:text-yellow-400`}
          >
            <svg className="w-full h-full fill-current" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
          </button>
        ))}
        <span className="ml-2 text-sm text-gray-600">({rating} star{rating !== 1 ? 's' : ''})</span>
      </div>
    );
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Suggest an Improvement</h2>
      
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">💡 Share Your Ideas</h3>
        <p className="text-blue-700 text-sm">
          Help us improve the community hood by sharing your innovative ideas and suggestions for new features or enhancements.
        </p>
      </div>

      {submitStatus && (
        <div className={`mb-4 p-4 rounded-lg ${
          submitStatus.type === 'success' 
            ? 'bg-green-50 border border-green-200 text-green-800' 
            : 'bg-red-50 border border-red-200 text-red-800'
        }`}>
          {submitStatus.message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            Suggestion Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., Community Events Calendar"
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Detailed Description *
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Explain your idea in detail, including how it would work and why it would be valuable..."
          />
        </div>

        {/* Expected Benefit */}
        <div>
          <label htmlFor="expected_benefit" className="block text-sm font-medium text-gray-700 mb-2">
            Expected Benefit
          </label>
          <textarea
            id="expected_benefit"
            name="expected_benefit"
            value={formData.expected_benefit}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="How would this suggestion benefit the community? What problems would it solve?"
          />
        </div>

        {/* Category */}
        <div>
          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
            Category *
          </label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select a category</option>
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>

        {/* Interest Rating */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Interest Level
          </label>
          <p className="text-sm text-gray-600 mb-2">How interested are you in seeing this feature implemented?</p>
          <StarRating 
            rating={formData.rating} 
            onRatingChange={(rating) => setFormData(prev => ({ ...prev, rating }))}
          />
        </div>

        {/* Anonymous Option */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_anonymous"
            name="is_anonymous"
            checked={formData.is_anonymous}
            onChange={handleChange}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
          <label htmlFor="is_anonymous" className="ml-2 text-sm font-medium text-gray-700">
            Submit anonymously
          </label>
        </div>

        {/* User Information - Hidden if anonymous */}
        {!formData.is_anonymous && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="user_name" className="block text-sm font-medium text-gray-700 mb-2">
                Your Name
              </label>
              <input
                type="text"
                id="user_name"
                name="user_name"
                value={formData.user_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Your full name"
              />
            </div>

            <div>
              <label htmlFor="user_email" className="block text-sm font-medium text-gray-700 mb-2">
                Your Email
              </label>
              <input
                type="email"
                id="user_email"
                name="user_email"
                value={formData.user_email}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="your.email@example.com"
              />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div>
          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-3 px-4 rounded-md text-white font-medium transition-colors ${
              isSubmitting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2'
            }`}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Suggestion'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SuggestionsForm;