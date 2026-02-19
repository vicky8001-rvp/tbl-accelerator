import numpy as np
import time

class TBLSimulator:
    def __init__(self):
        # Economic constituents (7)
        self.econ_factors = {
            'profitability': 1.0,
            'competitiveness': 1.0,
            'cost_reduction': 1.0,
            'brand_value': 1.0,
            'spin_offs': 1.0,
            'financial_benefits': 1.0,
            'trade_offs': 1.0
        }
        # Social constituents (7)
        self.social_factors = {
            'org_support': 1.0,
            'shared_ambition': 1.0,
            'long_term_perspective': 1.0,
            'commitment': 1.0,
            'corporate_culture': 1.0,
            'reputation': 1.0,
            'reporting': 1.0
        }
        # Environmental constituents (6)
        self.env_factors = {
            'carbon_footprint': 1.0,
            'climate_initiatives': 1.0,
            'efficiency_programs': 1.0,
            'product_dematerialization': 1.0,
            'carbon_labeling': 1.0,
            'biodiversity': 1.0
        }
        self.n_econ = len(self.econ_factors)
        self.n_social = len(self.social_factors)
        self.n_env = len(self.env_factors)

    def standard_run(self, months, invest_rate, random_seed=42):
        """Pure Python loop (baseline)"""
        np.random.seed(random_seed)
        # Convert to lists for faster access (still Python loop)
        econ = list(self.econ_factors.values())
        social = list(self.social_factors.values())
        env = list(self.env_factors.values())

        results = []
        for m in range(months):
            # Economic: small random walk
            for i in range(self.n_econ):
                econ[i] *= (1 + np.random.normal(0.02, 0.01))
            # Social: influenced by investment
            for i in range(self.n_social):
                social[i] *= (1 + invest_rate * np.random.random())
            # Environmental: influenced by social average
            social_avg = sum(social) / self.n_social
            for i in range(self.n_env):
                env[i] *= (1 + 0.05 * social_avg * invest_rate * np.random.random())
            # Record averages
            results.append({
                'month': m+1,
                'economic': sum(econ)/self.n_econ,
                'social': sum(social)/self.n_social,
                'environmental': sum(env)/self.n_env
            })
        return results

    def numpy_run(self, months, invest_rate, random_seed=42):
        """Vectorized NumPy version"""
        np.random.seed(random_seed)
        # Pre-allocate arrays
        econ = np.ones((months, self.n_econ))
        social = np.ones((months, self.n_social))
        env = np.ones((months, self.n_env))

        # Generate random shocks in bulk
        econ_shocks = 1 + np.random.normal(0.02, 0.01, (months-1, self.n_econ))
        social_shocks = 1 + invest_rate * np.random.random((months-1, self.n_social))
        # Cumulative products
        econ[1:] = econ[0] * np.cumprod(econ_shocks, axis=0)
        social[1:] = social[0] * np.cumprod(social_shocks, axis=0)

        # Environmental depends on social average each month (cannot fully vectorize)
        social_avg = np.mean(social, axis=1)
        for i in range(1, months):
            env[i] = env[i-1] * (1 + 0.05 * social_avg[i] * invest_rate * np.random.random(self.n_env))

        # Compute average scores per month
        econ_avg = np.mean(econ, axis=1)
        social_avg = np.mean(social, axis=1)
        env_avg = np.mean(env, axis=1)

        results = [{'month': i+1, 'economic': econ_avg[i], 'social': social_avg[i], 'environmental': env_avg[i]}
                   for i in range(months)]
        return results

    def tensorflow_run(self, months, invest_rate, random_seed=42):
        """TensorFlow version (GPU if available)"""
        import tensorflow as tf
        tf.random.set_seed(random_seed)
        # Use TensorFlow for vectorized operations
        # For simplicity, we'll implement the same logic as numpy but with tf ops
        # This can run on GPU automatically
        econ = tf.ones((months, self.n_econ), dtype=tf.float64)
        social = tf.ones((months, self.n_social), dtype=tf.float64)
        env = tf.ones((months, self.n_env), dtype=tf.float64)

        econ_shocks = 1 + tf.random.normal((months-1, self.n_econ), mean=0.02, stddev=0.01, dtype=tf.float64)
        social_shocks = 1 + invest_rate * tf.random.uniform((months-1, self.n_social), dtype=tf.float64)

        # Cumulative product (custom loop because tf.cumprod is 1D per column, we can do manually)
        # Simpler: use numpy within tf.function? No, we want graph. We'll do a loop (still fast on GPU)
        for i in tf.range(1, months):
            econ = tf.tensor_scatter_nd_update(econ, [[i]], [econ[i-1] * econ_shocks[i-1]])
            social = tf.tensor_scatter_nd_update(social, [[i]], [social[i-1] * social_shocks[i-1]])

        social_avg = tf.reduce_mean(social, axis=1)
        for i in tf.range(1, months):
            env = tf.tensor_scatter_nd_update(env, [[i]], [env[i-1] * (1 + 0.05 * social_avg[i] * invest_rate * tf.random.uniform((self.n_env,), dtype=tf.float64))])

        econ_avg = tf.reduce_mean(econ, axis=1).numpy()
        social_avg = tf.reduce_mean(social, axis=1).numpy()
        env_avg = tf.reduce_mean(env, axis=1).numpy()

        results = [{'month': i+1, 'economic': econ_avg[i], 'social': social_avg[i], 'environmental': env_avg[i]}
                   for i in range(months)]
        return results

    def benchmark(self, months=1200, invest_rate=0.1):
        """Run all three versions and return timing"""
        times = {}
        # Standard
        start = time.time()
        self.standard_run(months, invest_rate)
        times['Python (loop)'] = time.time() - start

        # NumPy
        start = time.time()
        self.numpy_run(months, invest_rate)
        times['NumPy'] = time.time() - start

        # TensorFlow (if available)
        try:
            start = time.time()
            self.tensorflow_run(months, invest_rate)
            times['TensorFlow'] = time.time() - start
        except Exception as e:
            times['TensorFlow'] = None
        return times