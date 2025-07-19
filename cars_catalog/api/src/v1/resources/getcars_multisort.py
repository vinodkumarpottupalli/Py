import os
from flask import jsonify, make_response, request
from flask_restful import Resource, Api
from api.models.models import Car
from sqlalchemy import and_, text


class GetCarsByMultiSort(Resource):
    def get(self):
        """
        Get the cars details by pagination and multiple sorting
        Accepted url parms below
        page: page number
        size: no of items in page
        brand: brand of the car
        model: model of the car
        transmission: transmission of the car
        price_operator: price_operator of the car ex: lte, gte and between
        price: price of the car
        price_max: maximum price of the car
        sort_by: sorting with above label and use comma separated
        sort_direction: sorting asc or desc; default asc
        """
        try:
            page = request.args.get('page', 1, type = int)
            size = request.args.get('size', 10, type = int)
            brand = request.args.get('brand', '%')
            model = request.args.get('model', '%')
            transmission = request.args.get    ('transmission', '%')
        
            price_operator = request.args.get('price_operator')
            price_value = request.args.get('price', 0, type = int)
            price_max_value = request.args.get('price_max', price_value + 1, type = int)

            sort_by = request.args.get('sort_by')
            sort_direction = request.args.get('sort_direction', 'asc')

            query = Car.query
        
            query = query.filter( \
                    and_( \
                        Car.brand.ilike('%' + brand + '%'), \
                        Car.model.ilike('%' + model + '%'), \
                        Car.transmission.ilike('%' + transmission + '%') \
                    ) \
                ) \

            if price_operator == 'lte':
                query = query.filter(Car.price <= price_value)
            elif price_operator == 'gte':
                query = query.filter(Car.price >= price_value)
            elif price_operator == 'between':
                query = query.filter(Car.price >= price_value, Car.price <= price_max_value)


            list_sort_by = sort_by.split(',')
            list_sort_direction = sort_direction.split(',')

            diff = len(list_sort_by) - len(list_sort_direction)

            for x in range(diff):
                list_sort_direction.append('asc')

            sort_columns = []

            for idx, sb in enumerate(list_sort_by):
                sort_columns.append(sb + ' ' + list_sort_direction[idx])

            query = query.order_by( text(','.join(sort_columns)) )

            cars = query.paginate(page = page, per_page = size)

            cars_response = [car.to_json() for car in cars.items]

            return make_response(jsonify({
                'data': cars_response, 
                'page': page, 
                'size': size, 
                'total_elements': cars.total, 
                'total_page': cars.pages
            }), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 400)